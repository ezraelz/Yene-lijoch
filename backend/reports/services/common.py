def get_church_for_user(user):
    """
    Return the church associated with the authenticated user.
    """

    if not hasattr(user, "profile"):
        return None

    return user.profile.church
