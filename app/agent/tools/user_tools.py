"""User-related agent tools."""

from langchain_core.tools import tool

from app.models.user import User
from app.agent.tools.base import ToolContext


@tool
def get_user_tool(user_identifier: str) -> str:
    """Use this tool to get information about a specific user. user_identifier: Name or email (partial match supported)."""
    if not ToolContext.db or not ToolContext.current_user:
        return "Error: Database context not available."

    db = ToolContext.db
    current_user = ToolContext.current_user

    user = (
        db.query(User)
        .filter(
            User.organization_id == current_user.organization_id,
            (User.full_name.ilike(f"%{user_identifier}%"))
            | (User.email.ilike(f"%{user_identifier}%")),
        )
        .first()
    )

    if not user:
        return f"❌ User matching '{user_identifier}' not found."

    return (
        f"👤 **{user.full_name}** (ID: {user.id})\n"
        f"Email: {user.email}\n"
        f"Role: {user.role.value}\n"
        f"Active: {'Yes' if user.is_active else 'No'}"
    )


@tool
def list_users_tool(role_filter: str = "") -> str:
    """Use this tool to list users in the organization. role_filter: Optional filter by role ('admin', 'manager', 'member')."""
    if not ToolContext.db or not ToolContext.current_user:
        return "Error: Database context not available."

    db = ToolContext.db
    current_user = ToolContext.current_user

    from app.models.user import UserRole

    query = db.query(User).filter(User.organization_id == current_user.organization_id)

    if role_filter:
        role_map = {
            "admin": UserRole.ADMIN,
            "manager": UserRole.MANAGER,
            "member": UserRole.MEMBER,
        }
        if role_filter.lower() in role_map:
            query = query.filter(User.role == role_map[role_filter.lower()])

    users = query.limit(10).all()

    if not users:
        return "No users found."

    lines = []
    for u in users:
        lines.append(f"• {u.full_name} ({u.email}) - {u.role.value}")

    return f"👥 Found {len(users)} users:\n" + "\n".join(lines)


@tool
def create_user_tool(
    email: str,
    full_name: str,
    password: str,
    role: str = "member",
) -> str:
    """Use this tool to create a new user. Admin/Manager only. email: User email, full_name: Full name, password: Initial password, role: 'admin', 'manager', or 'member'."""
    if not ToolContext.db or not ToolContext.current_user:
        return "Error: Database context not available."

    db = ToolContext.db
    current_user = ToolContext.current_user

    from app.models.user import UserRole
    from app.core.security import get_password_hash

    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        return "❌ You don't have permission to create users."

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return f"❌ User with email '{email}' already exists."

    role_map = {
        "admin": UserRole.ADMIN,
        "manager": UserRole.MANAGER,
        "member": UserRole.MEMBER,
    }
    user_role = role_map.get(role.lower(), UserRole.MEMBER)

    new_user = User(
        email=email,
        full_name=full_name,
        hashed_password=get_password_hash(password),
        role=user_role,
        organization_id=current_user.organization_id,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return f"✅ Created user '{new_user.full_name}' ({new_user.email}) with role {user_role.value}"


@tool
def update_user_tool(
    user_identifier: str,
    new_name: str = "",
    new_role: str = "",
    is_active: str = "",
) -> str:
    """Use this tool to update a user. user_identifier: Name or email, new_name: New full name (optional), new_role: New role (optional), is_active: 'true' or 'false' (optional)."""
    if not ToolContext.db or not ToolContext.current_user:
        return "Error: Database context not available."

    db = ToolContext.db
    current_user = ToolContext.current_user

    from app.models.user import UserRole

    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        return "❌ You don't have permission to update users."

    user = (
        db.query(User)
        .filter(
            User.organization_id == current_user.organization_id,
            (User.full_name.ilike(f"%{user_identifier}%"))
            | (User.email.ilike(f"%{user_identifier}%")),
        )
        .first()
    )

    if not user:
        return f"❌ User matching '{user_identifier}' not found."

    updates = []
    if new_name:
        user.full_name = new_name
        updates.append(f"name → '{new_name}'")

    if new_role:
        role_map = {
            "admin": UserRole.ADMIN,
            "manager": UserRole.MANAGER,
            "member": UserRole.MEMBER,
        }
        if new_role.lower() in role_map:
            user.role = role_map[new_role.lower()]
            updates.append(f"role → '{new_role}'")

    if is_active:
        user.is_active = is_active.lower() == "true"
        updates.append(f"active → {user.is_active}")

    if not updates:
        return "❌ No updates provided."

    db.commit()
    return f"✅ Updated user '{user.full_name}': {', '.join(updates)}"


user_tools = [
    get_user_tool,
    list_users_tool,
    create_user_tool,
    update_user_tool,
]
