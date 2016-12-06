from . import controller
from . import jsonapi


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('frontend', choices=('controller', 'jsonapi'))
    args = parser.parse_args()
    if args.frontend == 'controller':
        controller.main()
    elif args.frontend == 'jsonapi':
        jsonapi.main()
