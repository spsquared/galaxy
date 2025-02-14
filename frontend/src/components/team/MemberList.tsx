import type React from "react";
import type { UserPublic } from "../../api/_autogen";
import { useCurrentUser } from "../../contexts/CurrentUserContext";
import { Link } from "react-router-dom";

interface MemberListProps {
  members: UserPublic[];
  className?: string;
}

interface UserRowProps {
  user: UserPublic;
  isCurrentUser?: boolean;
}
const UserRow: React.FC<UserRowProps> = ({ user, isCurrentUser = false }) => (
  <Link to={`/user/${user.id}`}>
    <div className="flex flex-row items-center rounded">
      <img
        className="h-8 w-8 rounded-full bg-blue-100"
        src={user.profile?.avatar_url ?? "/default_profile_picture.png"}
      />

      <div className="ml-6 font-semibold">
        {user.username}
        {isCurrentUser && (
          <span className="ml-1 font-normal text-gray-600">(you)</span>
        )}
        {user.is_staff && (
          <span className="ml-1 font-normal text-gray-600">(staff)</span>
        )}
      </div>
      <div className="ml-12 flex-1 overflow-hidden overflow-ellipsis whitespace-nowrap text-end text-gray-600">
        {user.profile?.school}
      </div>
    </div>
  </Link>
);

// Displays a list of the users in members. If the current user is in members,
// displays the current user first.
const MemberList: React.FC<MemberListProps> = ({ members, className = "" }) => {
  const { user: currentUser } = useCurrentUser();
  return (
    <div className={`flex flex-col gap-2 ${className}`}>
      {/* display current user first */}
      {currentUser.isSuccess &&
        members.find((user) => user.id === currentUser.data.id) !==
          undefined && <UserRow isCurrentUser user={currentUser.data} />}
      {members.map(
        (member) =>
          member.id !== currentUser.data?.id && (
            <UserRow key={member.id} user={member} />
          ),
      )}
    </div>
  );
};

export default MemberList;
