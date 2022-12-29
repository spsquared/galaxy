import React, { Component } from "react";

import PaginationControl from "./paginationControl";
import Spinner from "./spinner";

class RankingTeamList extends Component {
  state = {
    pendingRequests: {},
    successfulRequests: {},
    showTeamID: null,
  };

  onTeamRequest = (teamId) => {
    const { state } = this;
    if (state.pendingRequests[teamId]) {
      return;
    }

    this.setState((prevState) => {
      return {
        pendingRequests: {
          ...prevState.pendingRequests,
          [teamId]: true,
        },
      };
    });
    Api.requestScrimmage(this.props.episode, teamId, (success) =>
      this.onRequestFinish(teamId, success)
    );
  };

  onRequestFinish = (teamId, success) => {
    this.setState((prevState) => {
      return {
        pendingRequests: {
          ...prevState.pendingRequests,
          [teamId]: false,
        },
        successfulRequests: success && {
          ...prevState.successfulRequests,
          [teamId]: true,
        },
      };
    });
    if (success) {
      this.props.onRequestSuccess();
      setTimeout(() => this.successTimeoutRevert(teamId), SUCCESS_TIMEOUT);
    }
  };

  successTimeoutRevert = (teamId) => {
    this.setState((prevState) => {
      return {
        successfulRequests: {
          ...prevState.successfulRequests,
          [teamId]: false,
        },
      };
    });
  };

  redirectToTeamPage = (team_id) => {
    this.props.history.push(`/${this.props.episode}/rankings/${team_id}`);
  };

  render() {
    const { props, state } = this;

    if (!this.props.loading && props.teams.length === 0) {
      return (
        <div className="card">
          <div className="header">
            <h4 className="title">No Teams Found!</h4>
            <br />
          </div>
        </div>
      );
    } else {
      const teamRows = props.teams.map((team) => {
        let buttonContent = "Request";
        if (state.pendingRequests[team.id]) {
          buttonContent = <i className="fa fa-circle-o-notch fa-spin"></i>;
        } else if (state.successfulRequests[team.id]) {
          buttonContent = <i className="fa fa-check"></i>;
        }
        return (
          <tr
            key={team.id}
            onClick={() => this.redirectToTeamPage(team.id)}
            class="page-item"
          >
            {<td>{Math.round(team.profile.rating)}</td>}
            <td>{team.name}</td>
            <td>{team.members.map((member) => member.username).join(", ")}</td>
            {<td>{team.profile.quote}</td>}
            <td>
              {this.props.episode_info.eligibility_criteria.map((criterion) => {
                const eligible = team.profile.eligible_for.includes(
                  criterion.id
                );
                return (
                  <span key={criterion.id}>
                    {eligible ? criterion.icon : ""}
                  </span>
                );
              })}
            </td>
            <td>{team.auto_accept_unranked ? "Yes" : "No"}</td>
            {true && (
              <td>
                <button
                  className="btn btn-xs"
                  onClick={(event) => {
                    event.stopPropagation();
                    this.onTeamRequest(team.id);
                  }}
                >
                  {buttonContent}
                </button>{" "}
              </td>
            )}
          </tr>
        );
      });

      return (
        <div>
          <div className="card">
            <div className="header">
              <h4 className="title">Rankings</h4>
            </div>
            <div className="content table-responsive table-full-width">
              <table className="table table-striped">
                <thead>
                  <tr>
                    <th>Rating</th>
                    <th>Team</th>
                    <th>Members</th>
                    <th>Quote</th>
                    <th>Eligibility</th>
                    <th>Auto-Accept</th>
                  </tr>
                </thead>
                <tbody>{!this.props.loading && teamRows}</tbody>
              </table>
              {this.props.loading && <Spinner />}
            </div>
          </div>
          <PaginationControl
            page={props.page}
            pageLimit={props.pageLimit}
            onPageClick={props.onPageClick}
          />
        </div>
      );
    }
  }
}

export default RankingTeamList;
