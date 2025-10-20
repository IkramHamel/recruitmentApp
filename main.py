from src.cmd.main import start_app
from src import migrate_permissions
from src.api import APIServer


if __name__ == '__main__':
    migrate_permissions()
    start_app()
    
app = APIServer().app