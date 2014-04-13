diaryApp = angular.module('diaryApp', ['diaryServices', 'ngSanitize'])

diaryApp.controller('EntriesCtrl', ['$scope', 'Entry', ($scope, Entry) ->
  $scope.getFormattedEntryDate = (entry) ->
    #TODO use external library for this
    if not entry._date?
      entry._date = new Date(entry.timestamp*1000)
    return "#{entry._date.toDateString()} #{entry._date.toLocaleTimeString()}"

  $scope.entries = Entry.recent({q:'hello', fields:'timestamp,html,wordcount,id'})

  $scope.days = ->
    days = []
    for entry in $scope.entries
      if not entry._date?
        entry._date = new Date(entry.timestamp*1000)
      day = entry._date.toLocaleDateString()
      days.push(day) if day not in days
    return days
])
