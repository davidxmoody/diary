diaryServices = angular.module('diaryServices', ['ngResource'])

diaryServices.factory('Entry', ['$resource', ($resource) ->
  return $resource('/entries/:entryId', {}, {
    recent: { method: 'GET', isArray: true, params: { order: 'desc', offset: 0, limit: 10 } }
    search: { method: 'GET', isArray: true, params: { order: 'desc', offset: 0, limit: 10 } }
  })
])
