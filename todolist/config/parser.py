import argparse


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='TodoList Application')
    parser.add_argument('-e', '--env', 
                      choices=['local', 'stage', 'live', 'test'], 
                      default='local',
                      help='Environment to run the application in (default: local)')
    return parser.parse_args()
