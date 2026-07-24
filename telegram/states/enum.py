from enum import StrEnum


class State(StrEnum):

    # Profile Add
    PROFILE_ADD_NAME = "profile_add_name"
    PROFILE_ADD_TYPE = "profile_add_type"
    PROFILE_ADD_GENERATION = "profile_add_generation"
    PROFILE_ADD_BIRTH_DATE = "profile_add_birth_date"
    PROFILE_ADD_X_USERNAME = "profile_add_x_username"
    PROFILE_ADD_INSTAGRAM_USERNAME = "profile_add_instagram_username"
    PROFILE_ADD_INSTAGRAM_USER_ID = "profile_add_instagram_user_id"
    PROFILE_ADD_TIKTOK_USERNAME = "profile_add_tiktok_username"

    # Profile Edit
    PROFILE_EDIT_SELECT = "profile_edit_select"
    PROFILE_EDIT_FIELD = "profile_edit_field"
    PROFILE_EDIT_VALUE = "profile_edit_value"

    # Profile Delete
    PROFILE_DELETE_SELECT = "profile_delete_select"
    PROFILE_DELETE_CONFIRM = "profile_delete_confirm"

    # Cookie Add
    COOKIE_ADD_WORKER = "cookie_add_worker"
    COOKIE_ADD_NAME = "cookie_add_name"
    COOKIE_ADD_CONTENT = "cookie_add_content"

    # Cookie Edit
    COOKIE_EDIT_WORKER = "cookie_edit_worker"
    COOKIE_EDIT_NAME = "cookie_edit_name"
    COOKIE_EDIT_CONTENT = "cookie_edit_content"

    # Cookie Delete
    COOKIE_DELETE_WORKER = "cookie_delete_worker"
    COOKIE_DELETE_NAME = "cookie_delete_name"
    COOKIE_DELETE_CONFIRM = "cookie_delete_confirm"

    # Cookie Test
    COOKIE_TEST_WORKER = "cookie_test_worker"
    COOKIE_TEST_NAME = "cookie_test_name"

    # Scraper
    SCRAPER_START = "scraper_start"
    SCRAPER_STOP = "scraper_stop"