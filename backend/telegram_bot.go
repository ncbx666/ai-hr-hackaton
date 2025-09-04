package main

import (
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"

	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
)

// HR отправляет команду /invite <user_id> <имя> <дата> <ссылка>
func main() {
	botToken := os.Getenv("TELEGRAM_BOT_TOKEN")
	if botToken == "" {
		log.Fatal("TELEGRAM_BOT_TOKEN env required")
	}
	bot, err := tgbotapi.NewBotAPI(botToken)
	if err != nil {
		log.Panic(err)
	}
	bot.Debug = true
	log.Printf("Authorized on account %s", bot.Self.UserName)

	u := tgbotapi.NewUpdate(0)
	u.Timeout = 60
	updates := bot.GetUpdatesChan(u)

	for update := range updates {
		if update.Message != nil && update.Message.IsCommand() {
			if update.Message.Command() == "invite" {
				args := strings.Split(update.Message.CommandArguments(), " ")
				if len(args) < 4 {
					bot.Send(tgbotapi.NewMessage(update.Message.Chat.ID, "Ошибка: используйте /invite <user_id> <имя> <дата> <ссылка>"))
					continue
				}
				userID, err := strconv.ParseInt(args[0], 10, 64)
				if err != nil {
					bot.Send(tgbotapi.NewMessage(update.Message.Chat.ID, "Ошибка: user_id должен быть числом"))
					continue
				}
				name := args[1]
				date := args[2]
				link := args[3]
				msg := tgbotapi.NewMessage(userID, fmt.Sprintf("Вас приглашают на собеседование!\nИмя: %s\nДата: %s\nСсылка: %s", name, date, link))
				// Кнопка подтверждения
				confirmBtn := tgbotapi.NewInlineKeyboardButtonData("Подтвердить", "confirm:"+fmt.Sprint(update.Message.Chat.ID))
				msg.ReplyMarkup = tgbotapi.NewInlineKeyboardMarkup(
					[]tgbotapi.InlineKeyboardButton{confirmBtn},
				)
				bot.Send(msg)
				bot.Send(tgbotapi.NewMessage(update.Message.Chat.ID, "Приглашение отправлено кандидату."))
			}
		}
		if update.CallbackQuery != nil {
			if strings.HasPrefix(update.CallbackQuery.Data, "confirm:") {
				hrID, _ := strconv.ParseInt(update.CallbackQuery.Data[8:], 10, 64)
				bot.Send(tgbotapi.NewMessage(update.CallbackQuery.Message.Chat.ID, "Спасибо, ваше собеседование подтверждено!"))
				bot.Send(tgbotapi.NewMessage(hrID, "Кандидат подтвердил участие в собеседовании."))
			}
		}
	}
}
