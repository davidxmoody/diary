diaryApp = angular.module('diaryApp', ['diaryServices', 'ngSanitize'])

diaryApp.controller('EntriesCtrl', ['$scope', 'Entry', ($scope, Entry) ->
  $scope.entries = Entry.search({q:'hello', fields:'date,html,wordcount,id'})

  $scope.days = ->
    return _.pluck($scope.entries, 'date')
])
