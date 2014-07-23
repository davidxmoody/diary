diaryApp = angular.module('diaryApp', ['diaryServices', 'ngSanitize'])

diaryApp.controller('EntriesCtrl', ['$scope', 'Entry', ($scope, Entry) ->
  $scope.getFormattedEntryDate = (entry) ->
    moment.unix(entry.timestamp).format('ddd DD MMM YYYY HH:mm')

  $scope.entries = Entry.recent({limit:50, fields:'timestamp,html,wordcount,id'})

  $scope.days = ->
    days = []
    for entry in $scope.entries
      day = moment.unix(entry.timestamp).format('YYYY-MM-DD')
      days.push(day) if day not in days
    return days
])
