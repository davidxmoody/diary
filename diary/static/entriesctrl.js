// Generated by CoffeeScript 1.4.0
(function() {
  var diaryApp,
    __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  diaryApp = angular.module('diaryApp', ['diaryServices', 'ngSanitize']);

  diaryApp.controller('EntriesCtrl', [
    '$scope', 'Entry', function($scope, Entry) {
      $scope.getFormattedEntryDate = function(entry) {
        return moment.unix(entry.timestamp).format('ddd DD MMM YYYY HH:mm');
      };
      $scope.entries = Entry.recent({
        limit: 50,
        fields: 'timestamp,html,wordcount,id'
      });
      return $scope.days = function() {
        var day, days, entry, _i, _len, _ref;
        days = [];
        _ref = $scope.entries;
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          entry = _ref[_i];
          day = moment.unix(entry.timestamp).format('YYYY-MM-DD');
          if (__indexOf.call(days, day) < 0) {
            days.push(day);
          }
        }
        return days;
      };
    }
  ]);

}).call(this);