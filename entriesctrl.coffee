diaryApp = angular.module('diaryApp', ['diaryServices', 'ngSanitize'])

diaryApp.controller 'EntriesCtrl', ['$scope', 'Entry', ($scope, Entry) ->
  $scope.entries = Entry.query()

  $scope.days = [
    '2014-03-19'
    '2014-03-20'
  ]
]
