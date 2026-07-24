from telegram.ext import (
    CommandHandler,
    ConversationHandler,
)

from bots.admin.auth import admin

from bots.admin.features.start import start
from bots.admin.features.cancel import cancel

from bots.admin.features.profile.list import profile_list
from bots.admin.features.profile import (
    add as profile_add,
    edit as profile_edit,
    delete as profile_delete,
)

from bots.admin.features.cookie.list import cookie_list
from bots.admin.features.cookie import (
    add as cookie_add,
    edit as cookie_edit,
    delete as cookie_delete,
    test as cookie_test,
)

from bots.admin.features.scraper.status import scraper_status
from bots.admin.features.scraper import (
    start as scraper_start,
    stop as scraper_stop,
)


def register_commands(app):

    profile_add_entry_points, profile_add_states = profile_add.get_conversation()
    profile_edit_entry_points, profile_edit_states = profile_edit.get_conversation()
    profile_delete_entry_points, profile_delete_states = profile_delete.get_conversation()

    cookie_add_entry_points, cookie_add_states = cookie_add.get_conversation()
    cookie_edit_entry_points, cookie_edit_states = cookie_edit.get_conversation()
    cookie_delete_entry_points, cookie_delete_states = cookie_delete.get_conversation()
    cookie_test_entry_points, cookie_test_states = cookie_test.get_conversation()

    scraper_start_entry_points, scraper_start_states = scraper_start.get_conversation()
    scraper_stop_entry_points, scraper_stop_states = scraper_stop.get_conversation()

    # General
    app.add_handler(
        CommandHandler(
            "start",
            admin(start),
        )
    )

    app.add_handler(
        CommandHandler(
            "cancel",
            admin(cancel),
        )
    )

    # List
    app.add_handler(
        CommandHandler(
            "profile_list",
            admin(profile_list),
        )
    )

    app.add_handler(
        CommandHandler(
            "cookie_list",
            admin(cookie_list),
        )
    )

    app.add_handler(
        CommandHandler(
            "scraper_status",
            admin(scraper_status),
        )
    )

    # Conversation
    app.add_handler(
        ConversationHandler(
            entry_points=[
                *profile_add_entry_points,
                *profile_edit_entry_points,
                *profile_delete_entry_points,
                *cookie_add_entry_points,
                *cookie_edit_entry_points,
                *cookie_delete_entry_points,
                *cookie_test_entry_points,
                *scraper_start_entry_points,
                *scraper_stop_entry_points,
            ],
            states={
                **profile_add_states,
                **profile_edit_states,
                **profile_delete_states,
                **cookie_add_states,
                **cookie_edit_states,
                **cookie_delete_states,
                **cookie_test_states,
                **scraper_start_states,
                **scraper_stop_states,
            },
            fallbacks=[
                CommandHandler(
                    "cancel",
                    admin(cancel),
                )
            ],
            allow_reentry=True,
        )
    )