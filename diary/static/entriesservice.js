// Generated by CoffeeScript 1.4.0
(function() {
  var diaryServices;

  diaryServices = angular.module('diaryServices', ['ngResource']);

  diaryServices.factory('Entry', [
    '$resource', function($resource) {
      return $resource('/entries/:entryId', {}, {
        recent: {
          method: 'GET',
          isArray: true,
          params: {
            order: 'desc',
            offset: 0,
            limit: 10
          }
        }
      });
    }
  ]);

}).call(this);
