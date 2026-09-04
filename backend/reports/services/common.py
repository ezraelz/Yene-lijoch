def get_organization_for_user(user):
    """
    Return the organization associated with the authenticated user.
    """

    if not hasattr(user, "profile"):
        return None

    return user.profile.organization
