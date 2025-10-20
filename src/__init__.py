from sqlalchemy.orm import Session
from src.db.session import SessionLocal
from .internal.iam.users.permissions import PERMISSIONS_USERRS 
from .internal.iam.roles.permissions import PERMISSIONS_ROLES 
from .internal.settings.app_settings.permissions import PERMISSIONS_APP
from .internal.anti_cheat.permissions import PERMISSIONS_ANTICHEAT
from .internal.exam.questions.permissions import PERMISSIONS_QUESTIONS
from .internal.exam.test.permissions import PERMISSIONS_TESTS
from .internal.exam.assessment.permissions import PERMISSIONS_ASSESSMENT
from .internal.job_positions.permissions import PERMISSIONS_JOBS



ALL_PERMISSIONS = {**PERMISSIONS_USERRS, **PERMISSIONS_ROLES,**PERMISSIONS_ANTICHEAT,**PERMISSIONS_APP,
                   **PERMISSIONS_QUESTIONS,**PERMISSIONS_TESTS,**PERMISSIONS_ASSESSMENT,**PERMISSIONS_JOBS}

def migrate_permissions():
    db: Session = SessionLocal()
    try:
        from .internal.iam.permissions.models import Permission, GroupPermission

        existing_groups = {group.name: group for group in db.query(GroupPermission).all()}
        existing_permissions = {perm.name for perm in db.query(Permission).all()}

        for group_name, group_info in ALL_PERMISSIONS.items():
            group_description = group_info["description"]
            permissions_list = group_info.get("permissions", []) 

            # Créer le groupe s'il n'existe pas
            if group_name not in existing_groups:
                new_group = GroupPermission(
                    name=group_name,
                    description=group_description
                )
                db.add(new_group)
                db.flush()  # 👈 flush pour récupérer l'ID sans commit
                existing_groups[group_name] = new_group
                print(f" Group added: {group_name}")

            group = existing_groups[group_name]

            for perm in permissions_list:
                if perm["name"] not in existing_permissions:
                    new_permission = Permission(
                        name=perm["name"],
                        description=perm.get("description", "No description"),
                        group_id=group.id  # 👈 bien lié au bon groupe
                    )
                    db.add(new_permission)
                    print(f"    ➕ Permission added: {perm['name']}")

        db.commit()
        print(" Permissions migrated successfully!")
    except Exception as e:
        db.rollback()
        print(f" Error migrating permissions: {e}")
    finally:
        db.close()
