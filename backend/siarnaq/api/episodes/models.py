import random
import string

import structlog
from django.apps import apps
from django.db import models, transaction
from django.utils import timezone
from sortedm2m.fields import SortedManyToManyField

from siarnaq import bracket
from siarnaq.api.episodes.managers import EpisodeQuerySet, TournamentQuerySet

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

    bracket_id_private = models.SlugField(blank=True)
    """The ID of the associated private bracket, in the bracket service."""

    bracket_id_public = models.SlugField(blank=True)
    """The ID of the associated public bracket, in the bracket service."""

    objects = TournamentQuerySet.as_manager()

    def __str__(self):
        return self.name_short

    def get_potential_participants(self):
        """Returns the list of participants that would be entered in this tournament,
        if it were to start right now."""
        return (
            apps.get_model("teams", "Team")
            .objects.with_active_submission()
            .filter_eligible(self)
            .all()
            .order_by("-profile__rating__value")
        )

    def initialize(self):
        """
        Seed the tournament with eligible teams in order of decreasing rating,
        populate the brackets in the bracket service, and create TournamentRounds.
        """

        # For security by obfuscation,
        # and to allow easy regeneration of bracket,
        # create a random string to append to private bracket.
        # Note that name_short can be up to 32 chars
        # while bracket_id_private has a 50-char limit
        # (the default for SlugField).
        # "_priv" also takes some space too.
        # Thus be careful with length of key.
        key = "".join(
            random.choices(
                string.ascii_uppercase + string.ascii_lowercase + string.digits, k=12
            )
        )

        # Some bracket servers, such as Challonge, do not allow hyphens in IDs
        # so substitute them just in case
        bracket_id_public = f"{self.name_short}".replace("-", "_")
        bracket_id_private = f"{bracket_id_public}_{key}_priv".replace("-", "_")
        self.bracket_id_private = bracket_id_private
        self.bracket_id_public = bracket_id_public

        # First bracket made should be private,
        # to hide results and enable fixing accidents
        bracket.create_tournament(self, True)

        participants = self.get_potential_participants()

        bracket.bulk_add_participants(self, participants, True)
        bracket.start_tournament(bracket_id_private)

        round_indexes = bracket.get_round_indexes(bracket_id_private)

        # NOTE: rounds' order and indexes get weird in double elim.
        # Tracked in #548
        round_objects = [
            TournamentRound(
                tournament=self,
                bracket_id=round_index,
                name=f"Round {round_index}",
            )
            for round_index in round_indexes
        ]

        with transaction.atomic():
            TournamentRound.objects.bulk_create(round_objects)
            self.save(update_fields=["bracket_id_private", "bracket_id_public"])

    def report_for_tournament(self, match):
        """
        If a match is associated with a tournament bracket,
        update that tournament bracket.
        """

        bracket.update_match(self.bracket_id_private, match.bracket_id, match)


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

    # NOTE: this is not really an "ID" in the unique sense.
    # **It is not necessarily unique across all tournaments.**
    # You could rename this field,
    # but that's a very widespread code change and migration,
    # with low probability of success and high impact of failure.
    bracket_id = models.SmallIntegerField(null=True, blank=True)
    """The ID of this round as referenced by the bracket service."""

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
                fields=["tournament", "bracket_id"],
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

        num_maps = len(self.maps.all())
        # Sure, matches with even number of maps won't run.
        # But might as well fail fast.
        if num_maps % 2 == 0:
            raise RuntimeError("The round does not have an odd number of maps.")

        (
            match_objects,
            match_participant_objects,
        ) = bracket.get_match_and_participant_objects_for_round(
            self.tournament.bracket_id_private, self
        )

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
