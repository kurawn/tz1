from django.conf import settings
from django.core.management.base import BaseCommand
from telegram import Bot
from telegram.ext import Updater, Filters
from telegram.utils.request import Request
from telegram.ext import CommandHandler, MessageHandler
from telegram import InlineKeyboardButton
from telegram.ext import CallbackContext, ConversationHandler
from telegram import Update
from telegram import InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram import ParseMode, ForceReply
from telegram.ext import CallbackQueryHandler
from enum import Enum, auto

from ugc.models import Profile, Questionnaire
from ugc.gsheet import get_worksheets

CALLBACK_BUTTON1_START = "callback_button1_start"
CALLBACK_BUTTON_QUERY_1 = "callback_button_query_1"
CALLBACK_BUTTON_QUERY_2 = "callback_button_query_2"
CALLBACK_BUTTON_QUERY_3 = "callback_button_query_3"
CALLBACK_BUTTON_ANSWER = "callback_buttonanswer"

TITLES = {
    CALLBACK_BUTTON1_START: 'Пройти анкету',
    CALLBACK_BUTTON_QUERY_1: "Вариант №1",
    CALLBACK_BUTTON_QUERY_2: "Вариант №2",
    CALLBACK_BUTTON_QUERY_3: "Вариант №3",
    CALLBACK_BUTTON_ANSWER: 'Відповісти',
}
STAN = {
    '1': False,
    '2': False,
    '3': False,
}


def get_inline_keyboard():
    if STAN['1']:
        TITLES[CALLBACK_BUTTON_QUERY_1] = '✅ Вариант №1'
    else:
        TITLES[CALLBACK_BUTTON_QUERY_1] = 'Вариант №1'
    if STAN['2']:
        TITLES[CALLBACK_BUTTON_QUERY_2] = '✅ Вариант №2'
    else:
        TITLES[CALLBACK_BUTTON_QUERY_2] = 'Вариант №2'
    if STAN['3']:
        TITLES[CALLBACK_BUTTON_QUERY_3] = '✅ Вариант №3'
    else:
        TITLES[CALLBACK_BUTTON_QUERY_3] = 'Вариант №3'

    keyboard = [
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_QUERY_1], callback_data=CALLBACK_BUTTON_QUERY_1),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_QUERY_2], callback_data=CALLBACK_BUTTON_QUERY_2),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_QUERY_3], callback_data=CALLBACK_BUTTON_QUERY_3),
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_ANSWER], callback_data=CALLBACK_BUTTON_ANSWER),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def start_questionnaire(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_name = update.message.from_user.username
    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': user_name,
        }
    )
    context.user_data["chat_id"] = chat_id
    context.user_data["user_name"] = user_name

    keyboard = [
        [InlineKeyboardButton(TITLES[CALLBACK_BUTTON1_START], callback_data=CALLBACK_BUTTON1_START),
         ],
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Привіт',
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


class BotSteps(Enum):
    QuestionNumber = auto()
    Question = auto()


def question_name(update: Update, context: CallbackContext):
    query = update.callback_query

    chat_id = update.effective_message.chat_id
    current_text = update.effective_message.text

    query.edit_message_text(
        text=current_text,
        parse_mode=ParseMode.MARKDOWN,
    )

    context.bot.send_message(
        chat_id=chat_id,
        text="Введите Ваше имя",
        reply_markup=ForceReply(True)
    )
    return BotSteps.QuestionNumber


def question_number(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.user_data["name"] = update.message.text

    context.bot.send_message(
        chat_id=chat_id,
        text="Введите Ваш номер телефона",
        reply_markup=ForceReply(True)
    )
    return BotSteps.Question


def question(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.user_data["number"] = update.message.text
    context.bot.send_message(
        chat_id=chat_id,
        text="Выберите один или несколько вариантов ответа:",
        reply_markup=get_inline_keyboard(),
    )
    return ConversationHandler.END


def keyboard_callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    chat_id = update.effective_message.chat_id
    current_text = update.effective_message.text

    if data == CALLBACK_BUTTON_QUERY_1:
        STAN['1'] = not (STAN['1'])
        query.edit_message_text(
            text=current_text,
            reply_markup=get_inline_keyboard(),
        )
    elif data == CALLBACK_BUTTON_QUERY_2:
        STAN['2'] = not (STAN['2'])
        query.edit_message_text(
            text=current_text,
            reply_markup=get_inline_keyboard(),
        )
    elif data == CALLBACK_BUTTON_QUERY_3:
        STAN['3'] = not (STAN['3'])
        query.edit_message_text(
            text=current_text,
            reply_markup=get_inline_keyboard(),
        )
    elif data == CALLBACK_BUTTON_ANSWER:
        if STAN['1'] or STAN['2'] or STAN['3']:
            context.user_data["answer"] = ''
            if STAN['1']:
                context.user_data["answer"] += 'Вариант №1, '
                STAN['1'] = False
            if STAN['2']:
                context.user_data["answer"] += 'Вариант №2, '
                STAN['2'] = False
            if STAN['3']:
                context.user_data["answer"] += 'Вариант №3, '
                STAN['3'] = False

            context.user_data["answer"] = context.user_data["answer"][:-2] + '.'
            query.edit_message_text(
                text=current_text,
                parse_mode=ParseMode.MARKDOWN,
            )

            Questionnaire(
                chat_id=context.user_data["chat_id"],
                login_telegram=context.user_data["user_name"],
                reply_1=context.user_data["name"],
                reply_2=context.user_data["number"],
                reply_3=context.user_data["answer"],
            ).save()

            sheets_client = get_worksheets()
            wks = sheets_client.worksheet('Лист1')
            result = [
                context.user_data["chat_id"],
                context.user_data["user_name"],
                context.user_data["name"],
                context.user_data["number"],
                context.user_data["answer"],
                      ]
            wks.append_row(result)
            context.bot.send_message(
                chat_id=chat_id,
                text='Дякуюємо за пройдене опитування',
            )

        else:
            query.edit_message_text(
                text=current_text,
                parse_mode=ParseMode.MARKDOWN,
            )
            # Отправим новое сообщение при нажатии на кнопку
            context.bot.send_message(
                chat_id=chat_id,
                text="Вы не выбрали ни одного варианта. Выберите один или несколько вариантов ответа:",
                reply_markup=get_inline_keyboard(),
            )


def cancel(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Скасовано!',
        reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


class Command(BaseCommand):
    help = 'Телеграм-бот'

    def handle(self, *args, **options):
        request = Request(
            connect_timeout=0.5,
            read_timeout=1.0,
        )
        bot = Bot(
            request=request,
            token=settings.TOKEN_BOT,
        )

        updater = Updater(
            bot=bot,
            use_context=True,
        )

        print(bot.get_me())
        start_handler = CommandHandler('start', start_questionnaire)
        quest_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(question_name, pattern='callback_button1_start')],
            states={
                BotSteps.QuestionNumber: [
                    MessageHandler(Filters.text, question_number)
                ],
                BotSteps.Question: [
                    MessageHandler(Filters.text, question)
                ],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )
        buttons_handler = CallbackQueryHandler(callback=keyboard_callback_handler)
        updater.dispatcher.add_handler(start_handler)
        updater.dispatcher.add_handler(quest_handler)
        updater.dispatcher.add_handler(buttons_handler)
        updater.start_polling()
        updater.idle()
