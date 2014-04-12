diaryServices = angular.module('diaryServices', ['ngResource'])

constructor = ($resource) ->
  console.log 'running Entry constructor'
  return $resource('http://127.0.0.1:22022/entries/', {}, { query: {method: 'GET', isArray: true} })

diaryServices.factory('Entry', ['$resource', constructor])
