from .enums import PollingTypeEnum


polling_strings = {
	PollingTypeEnum.note.value: [
		"Вам помогли заметки сегодня?"
	],
	PollingTypeEnum.task.value: [
		"Сегодня у вас получилось выполнить поставленные перед собой задачи?"
	],
	PollingTypeEnum.health.value: [
		"Как с точки зрения здоровья вы себя чувствуете сегодня?"
	],
	PollingTypeEnum.mood.value: [
		"Что насчет настроения сегодня?"
	],
	PollingTypeEnum.next_day_expectations.value: [
		"Завтра ожидается хороший день?"
	]
}
