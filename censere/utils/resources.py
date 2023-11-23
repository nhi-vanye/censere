
def parse_resources( fields : list ) -> dict:
    """
    Parse a list of resources into a dict
    """
    resources = {}

    for field in fields:

        words = field.split("=")

        resources[ words[0].strip() ] = words[1].strip()

    return resources
