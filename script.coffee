window.EntriesCtrl = ($scope) ->
  $scope.helloText = 'hello world'
  $scope.entries = [
    {
        'id': '1383057333-unknown',
        'date': 1383057333,
        'wordcount': 17,
        'text': '''This is another new entry, wooo!

It has a #hashtag in it.

#plan This entry was edited.'''
    },
    {
        'id': '1296452400-unknown',
        'date': 1296452400,
        'wordcount': 97,
        'text': '''This is the first ever test entry. It has a #hashtag in it. 

#link Here is a super awesome link to [Google](http://www.google.com).

Here is some inline `monospace stuff`. And here is a simple list:

- One
- Two
- Three

And finally here is some quoted text:

> I'm quoted!

The standard chunk of Lorem Ipsum used since the 1500s is reproduced below for those interested. Sections 1.10.32 and 1.10.33 from "de Finibus Bonorum et Malorum" by Cicero are also reproduced in their exact original form, accompanied by English versions from the 1914 translation by H. Rackham.'''
    }
  ]

  $scope.days = [
    '2014-03-19'
    '2014-03-20'
  ]

