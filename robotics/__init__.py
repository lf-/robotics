def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('frontend', choices=('controller', 'jsonapi'))
    args = parser.parse_args()
    if args.frontend == 'controller':
        from . import controller
        controller.main()
    elif args.frontend == 'jsonapi':
        from . import jsonapi
        jsonapi.main()
