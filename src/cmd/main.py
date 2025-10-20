# cmd/main.py
import click
from src.app import Application


@click.command()
@click.option('--host', default='0.0.0.0', help='The host to bind the server to.')
@click.option('--port', default=8096, help='The port to run the server on.')
def start_app(host: str, port: int):
    
    """Start the FastAPI application."""
    # Initialize and run the application
    application = Application(host=host,port=port)
    application.run()
    

if __name__ == '__main__':
    start_app()
