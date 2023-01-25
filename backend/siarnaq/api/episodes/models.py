import uuid

import google.cloud.tasks_v2 as tasks_v2
import structlog
from django.apps import apps
from django.conf import settings
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from sortedm2m.fields import SortedManyToManyField

from siarnaq import bracket
from siarnaq.api.episodes.managers import EpisodeQuerySet, TournamentQuerySet
from siarnaq.gcloud import tasks

logger = structlog.get_logger(__name__)


class Language(models.TextChoices):
    """
    An immutable type enumerating the available languages.
    """

    JAVA_8 = "java8"
    PYTHON_3 = "py3"


class EligibilityCriterion(models.Model):
    """
    A database model for an eligibility criterion for entering into a tournament.
    """

    title = models.CharField(max_length=128)
    """The title of this criterion."""

    description = models.TextField()
    """The description of this criterion."""

    icon = models.CharField(max_length=8)
    """An icon to display for teams that satisfy this criterion."""

    def __str__(self):
        return self.title


class Episode(models.Model):
    """
    A database model for the information regarding an episode of Battlecode.
    """

    name_short = models.SlugField(max_length=16, primary_key=True)
    """Short unique identifying tag for the episode."""

    name_long = models.CharField(max_length=128)
    """Full-form name for the episode."""

    blurb = models.TextField(blank=True)
    """A longer description of the episode."""

    registration = models.DateTimeField()
    """
    The time at which registration for the episode begins.
    Before this time, the episode is only visible to staff users.
    """

    game_release = models.DateTimeField()
    """
    The time at which the game specs are released.
    Before this time, the game specs are only visible to staff users.
    """

    game_archive = models.DateTimeField()
    """
    The time at which the episode is archived.
    After this time, no more ranked matches can be played.
    """

    submission_frozen = models.BooleanField(default=True)
    """
    Whether submissions are frozen.
    If true, only teams with staff privileges can make submisssions.
    """

    autoscrim_schedule = models.CharField(max_length=64, null=True, blank=True)
    """A cron specification for the autoscrim schedule, or null if disabled."""

    language = models.CharField(max_length=8, choices=Language.choices)
    """The implementation language supported for this episode."""

    scaffold = models.URLField(blank=True)
    """The URL of the git repository where the scaffold can be obtained."""

    artifact_name = models.CharField(max_length=32, blank=True)
    """The name of the artifact generated by deploy systems."""

    release_version_public = models.CharField(max_length=32, blank=True)
    """The code release available for public use."""

    release_version_saturn = models.CharField(max_length=32, blank=True)
    """The code release used by Saturn, which may differ from the public version."""

    eligibility_criteria = models.ManyToManyField(
        EligibilityCriterion, related_name="episodes", blank=True
    )
    """The eligibility criteria active in this episode."""

    pass_requirement_win = models.PositiveSmallIntegerField(null=True, blank=True)
    """
    The minimum number of matches to be won within a specified window in order to pass
    the Battlecode class.
    """

    pass_requirement_out_of = models.PositiveSmallIntegerField(null=True, blank=True)
    """
    The size of the window in which a minimum number of matches must be won in order to
    pass the Battlecode class.
    """

    objects = EpisodeQuerySet.as_manager()

    def __str__(self):
        return self.name_short

    def frozen(self):
        """Return whether the episode is currently frozen to submissions."""
        now = timezone.now()
        if self.submission_frozen or now < self.game_release:
            return True
        return Tournament.objects.filter(
            episode=self,
            submission_freeze__lte=now,
            submission_unfreeze__gt=now,
            is_public=True,
        ).exists()

    def autoscrim(self, best_of):
        """
        Trigger a round of automatically-generated ranked scrimmages for all teams in
        this episode with an accepted submission, unless the episode is archived or
        frozen.

        Parameters
        ----------
        best_of : int
            The number of maps to be played in each match, must be no greater than the
            number of maps available for the episode.
        """
        log = logger.bind(episode=self.pk)
        if self.frozen():
            log.warn("autoscrim_frozen", message="Refusing to autoscrim: frozen.")
            return
        if timezone.now() > self.game_archive:
            log.warn("autoscrim_archived", message="Refusing to autoscrim: archived.")
        apps.get_model("teams", "Team").objects.autoscrim(episode=self, best_of=best_of)

    def for_saturn(self):
        """Return the representation of this object as expected by Saturn."""
        return {
            "name": self.name_short,
            "language": self.language,
            "scaffold": self.scaffold,
        }


class Map(models.Model):
    """
    A database model for the information regarding a game map in an episode.
    """

    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name="maps")
    """The episode to which this map belongs."""

    name = models.SlugField(max_length=24)
    """The name of the map."""

    is_public = models.BooleanField(default=False)
    """
    Whether the map is publicly accessible.
    If false, only teams with staff privileges can use the map.
    """

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["episode", "name"],
                name="map-unique-episode-name",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.episode})"


class TournamentStyle(models.TextChoices):
    """
    An immutable type enumerating the available styles of tournament.
    """

    SINGLE_ELIMINATION = "SE"
    DOUBLE_ELIMINATION = "DE"


class Tournament(models.Model):
    """
    A database model for the information regarding a tournament in an episode.
    """

    name_short = models.SlugField(max_length=32, primary_key=True)
    """Short unique identifying tag for the tournament."""

    name_long = models.CharField(max_length=128)
    """Full-form name for the tournament."""

    blurb = models.TextField(blank=True)
    """A longer description of the tournament."""

    episode = models.ForeignKey(
        Episode,
        on_delete=models.PROTECT,
        related_name="tournaments",
    )
    """The episode to which this tournament belongs."""

    style = models.CharField(max_length=2, choices=TournamentStyle.choices)
    """The style of this tournament."""

    eligibility_includes = models.ManyToManyField(
        EligibilityCriterion,
        related_name="include_tournaments",
        blank=True,
    )
    """
    The eligibility criteria that must be satisfied for a team to enter the tournament.
    """

    eligibility_excludes = models.ManyToManyField(
        EligibilityCriterion,
        related_name="exclude_tournaments",
        blank=True,
    )
    """
    The eligibility criteria that must not be satisfied for a team to enter the
    tournament.
    """

    require_resume = models.BooleanField()
    """Whether teams must have submitted resumes in order to enter the tournament."""

    is_public = models.BooleanField()
    """Whether this tournament is included in the public index."""

    display_date = models.DateField()
    """
    The official date of the tournament; that is, when it will be streamed.
    """

    submission_freeze = models.DateTimeField()
    """
    The time at which submissions are frozen for the tournament.
    Between this time and the unfreeze time, only staff members are able to submit.
    """

    submission_unfreeze = models.DateTimeField()
    """
    The time at which submissions are unfrozen for the tournament.
    Between the freeze time and this time, only staff members are able to submit.
    The submissions to enter into this tournament are the latest ones accepted by this
    time.
    """

    external_id_private = models.SlugField(max_length=128, blank=True)
    """The bracket service's ID of the associated private bracket."""

    external_id_public = models.SlugField(max_length=128, blank=True)
    """The bracket service's ID of the associated public bracket."""

    objects = TournamentQuerySet.as_manager()

    def __str__(self):
        return self.name_short

    def get_eligible_teams(self):
        """Returns the list of teams that would be entered in this tournament,
        if it were to start right now."""
        return (
            apps.get_model("teams", "Team")
            .objects.with_active_submission()
            .filter_eligible(self)
            .order_by("-profile__rating__value")
        )

    def initialize(self):
        """
        Seed the tournament with eligible teams in order of decreasing rating,
        populate the brackets in the bracket service, and create TournamentRounds.
        """

        # For security by obfuscation, and to allow easy regeneration of bracket,
        # create a random string to append to private bracket.
        key = str(uuid.uuid4())
        self.external_id_public = f"{self.name_short}"
        self.external_id_private = f"private_{self.external_id_public}_{key}"

        teams = self.get_eligible_teams()
        for is_private in [True, False]:
            bracket.create_tournament(self, is_private=is_private)
            bracket.bulk_add_teams(self, teams, is_private=is_private)
            bracket.start_tournament(self, is_private=is_private)

        # Create TournamentRound objects
        round_indexes = bracket.get_round_indexes(self, is_private=True)

        # NOTE: rounds' order and indexes get weird in double elim.
        # Tracked in #548
        round_objects = [
            TournamentRound(
                tournament=self,
                external_id=round_index,
                name=f"Round {round_index}",
            )
            for round_index in round_indexes
        ]

        with transaction.atomic():
            TournamentRound.objects.bulk_create(round_objects)
            self.save(update_fields=["external_id_private", "external_id_public"])


class ReleaseStatus(models.IntegerChoices):
    """
    An immutable type enumerating the degree to which the results of a tournament match
    are released. Greater values indicate greater visibility.
    """

    HIDDEN = 0
    PARTICIPANTS = 1
    RESULTS = 2


class TournamentRound(models.Model):
    """
    A database model for the information regarding a round of a tournament. A round is
    defined as a parallel set of matches; for example, "Round 1", or the semi-finals.
    """

    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.PROTECT,
        related_name="rounds",
    )
    """The tournament to which this round belongs."""

    external_id = models.SmallIntegerField(null=True, blank=True)
    """
    The bracket service's internal ID of this round.
    """

    name = models.CharField(max_length=64)
    """The name of this round in human-readable form, such as "Round 1"."""

    maps = SortedManyToManyField(Map, related_name="tournament_rounds", blank=True)
    """The maps to be used in this round."""

    release_status = models.IntegerField(
        choices=ReleaseStatus.choices, default=ReleaseStatus.HIDDEN
    )
    """THe degree to which matches in this round are released."""

    in_progress = models.BooleanField(default=False)
    """Whether the round is currently being run on the Saturn compute cluster."""

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tournament", "external_id"],
                name="round-unique-tournament-bracket",
            )
        ]

    def __str__(self):
        return f"{self.tournament} ({self.name})"

    def enqueue(self):
        """Creates and enqueues all matches for this round.
        Fails if this round is already in progress."""

        if self.in_progress:
            raise RuntimeError("The round's matches are already running in Saturn.")

        num_maps = self.maps.count()
        # Game runner allows for even number of maps.
        # But we can't allow this for tournaments, since this would result in ties.
        if num_maps % 2 == 0:
            raise RuntimeError("The round does not have an odd number of maps.")

        (
            match_objects,
            match_participant_objects,
        ) = bracket.get_match_and_participant_objects_for_round(self)

        Match = apps.get_model("compete", "Match")

        with transaction.atomic():
            matches = Match.objects.bulk_create(match_objects)
            # Can only create these objects after matches are saved,
            # because beforehand, matches will not have a pk.
            maps_for_match_objects = [
                Match.maps.through(match_id=match.pk, map_id=map.pk)
                for match in matches
                for map in self.maps.all()
            ]
            Match.maps.through.objects.bulk_create(maps_for_match_objects)
            apps.get_model("compete", "MatchParticipant").objects.bulk_create(
                match_participant_objects
            )

        Match.objects.filter(pk__in=[match.pk for match in matches]).enqueue()

        self.in_progress = True
        self.save(update_fields=["in_progress"])

    def request_publish_to_bracket(self, *, is_public):
        """Request that the match results are published asynchronously."""

        tasks_client = tasks.get_task_client()
        parent = tasks_client.queue_path(
            settings.GCLOUD_PROJECT,
            settings.GCLOUD_LOCATION,
            settings.GCLOUD_BRACKET_QUEUE,
        )
        for match in self.matches.all():
            url = "https://{}{}".format(
                settings.ALLOWED_HOSTS[0],
                reverse(
                    "match-publish-public-bracket",
                    kwargs={"pk": self.pk, "episode_id": self.tournament.episode.pk},
                ),
            )
            task = tasks_v2.Task(
                http_request=tasks_v2.HttpRequest(
                    http_method=tasks_v2.HttpMethod.POST,
                    url=url,
                    oidc_token=tasks_v2.OidcToken(
                        service_account_email=settings.GCLOUD_SERVICE_EMAIL,
                    ),
                ),
            )
            tasks_client.create_task(request=dict(parent=parent, task=task))

        self.release_status = ReleaseStatus.RESULTS
        self.save(update_fields=["release_status"])
