package main

import (
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"

	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
)

// HR отправляет команду /invite <user_id> <имя> <ссылка>
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
				   if len(args) < 3 {
					   bot.Send(tgbotapi.NewMessage(update.Message.Chat.ID, "Ошибка: используйте /invite <user_id> <имя> <ссылка>"))
					   continue
				   }
				   userID, err := strconv.ParseInt(args[0], 10, 64)
				   if err != nil {
					   bot.Send(tgbotapi.NewMessage(update.Message.Chat.ID, "Ошибка: user_id должен быть числом"))
					   continue
				   }
				   name := args[1]
				   link := args[2]
				   // Сохраняем связь между кандидатом и HR
				   if candidateToHR == nil {
					   candidateToHR = make(map[int64]int64)
				   }
				   candidateToHR[userID] = update.Message.Chat.ID
				   msg := tgbotapi.NewMessage(userID, fmt.Sprintf("Вас приглашают на собеседование!\nИмя: %s\nСсылка: %s\n\nПожалуйста, введите удобную дату и время собеседования в формате ДД.ММ.ГГГГ ЧЧ:ММ", name, link))
				   bot.Send(msg)
				   bot.Send(tgbotapi.NewMessage(update.Message.Chat.ID, "Приглашение отправлено кандидату. Ожидаем ответа с датой."))
			   }
		   }
		   // Обработка ответа кандидата с датой
		   if update.Message != nil && !update.Message.IsCommand() {
			   userID := update.Message.From.ID
			   if candidateToHR != nil {
				   hrID, ok := candidateToHR[userID]
				   if ok {
					   // Проверяем формат даты (очень простой, можно доработать)
					   dateText := update.Message.Text
					   // Пересылаем HR
					   bot.Send(tgbotapi.NewMessage(hrID, fmt.Sprintf("Кандидат выбрал дату собеседования: %s", dateText)))
					   // Сообщаем кандидату, что его дата отправлена HR
					   bot.Send(tgbotapi.NewMessage(userID, "Спасибо! Ваш вариант даты отправлен HR. Ожидайте подтверждения."))
					   // Можно добавить логику подтверждения от HR
				   }
			   }
		   }
	}
}
