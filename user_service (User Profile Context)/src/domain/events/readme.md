Command	Изменяет состояние системы, вызывает side effects	(AddTrackToFavourites)

Query	Чтение данных без изменения состояния. Ответ возвращается сразу.	(GetUserLikedTracks)

Event	Уведомление о уже произошедшем изменении. Может обрабатываться асинхронно.	(UserLikedTrack) (пост-фактум)