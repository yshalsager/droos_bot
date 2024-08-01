from telegram import ReplyKeyboardMarkup
from telegram.constants import InlineKeyboardMarkupLimit

from droos_bot import CONFIG, DATA_COLUMNS


def create_keyboard(  # noqa: PLR0913
    items: list[str],
    show_back: bool = True,
    show_pagination: bool = True,
    show_bullet: bool = True,
    current_page: int = 0,
    items_per_page: int = 10,
    max_pages_displayed: int = InlineKeyboardMarkupLimit.BUTTONS_PER_ROW - 3,
) -> ReplyKeyboardMarkup:
    """Generate pagination numbers with visual indicators.

    :param items: list of keyboard buttons
    :param show_back: Add back button to the keyboard
    :param show_pagination: Add pagination buttons
    :param show_bullet: Add bullet before each button
    :param current_page: The current page number (0-based).
    :param items_per_page: The number of items to display per page.
    :param max_pages_displayed: Max pages displayed (excl. first & last). Defaults to 5.
    :return: Pagination strings with indicators.

    Indicators:
      - 🔶 Current page
      - «  Before home (only if not on the first page)
      - »  After end (only if not on the last page)
      - ←  Before current page
      - →  After current page
    """
    total_pages = (len(items) + items_per_page - 1) // items_per_page
    current_page = current_page if current_page >= 0 else total_pages - 1
    # Calculate start and end pages for display
    half_display = max_pages_displayed // 2
    start_page = max(1, current_page + 1 - half_display)
    end_page = min(total_pages, start_page + max_pages_displayed)
    # Adjust start page if necessary to show max_pages_displayed pages
    if end_page - start_page < max_pages_displayed and start_page > 1:
        start_page = end_page - max_pages_displayed + 1

    pagination = []
    if show_pagination and total_pages > 1:
        # Add "«" if not on the first page
        if current_page > 0:
            pagination.append("«")

        for page in range(start_page, end_page + 1):
            if page == current_page + 1:
                pagination.append(f"🔶{page}")
            elif page < current_page + 1:
                pagination.append(f"←{page}")
            else:
                pagination.append(f"{page}→")

        # Add "»" if not on the last page
        if current_page < total_pages - 1:
            pagination.append("»")

    # slice data
    start_idx = current_page * items_per_page
    end_idx = start_idx + items_per_page
    keyboard = [[f"• {item}" if show_bullet else item] for item in items[start_idx:end_idx]]

    # finalize the keyboard
    bottom_row = ["القائمة الرئيسية 🏠"]
    if show_back:
        bottom_row.append("🔙 رجوع")
    if pagination:
        keyboard.append(pagination)
    keyboard.append(bottom_row)

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def create_main_keyboard() -> list[list[str]]:
    data_values = [
        [value] for key, value in DATA_COLUMNS.items() if key not in CONFIG.get("hide", [])
    ]
    main_keyboard_buttons = [*data_values]
    buttons_to_disable = CONFIG.get("disable", [])
    for item in ["إرسال مواد", "التواصل والاقتراحات", "البحث في المحتوى"]:
        if item not in buttons_to_disable:
            main_keyboard_buttons.append([item])
    return main_keyboard_buttons


main_keyboard = ReplyKeyboardMarkup(create_main_keyboard())
cancel_search_keyboard = ReplyKeyboardMarkup([["القائمة الرئيسية 🏠"], ["إلغاء البحث"]])
cancel_keyboard = ReplyKeyboardMarkup([["إنهاء"]])
