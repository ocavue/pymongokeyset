pymongokeyset: offset-free paging for pymongo
==================

Example
-----------

An executable example can be found at ``pymongokeyset/example/simple_examle.py``

.. code-block:: python

    collection = prepare()
    collection.insert_many([{'_id': i} for i in range(7)])

    search_condictions = {
        'collection': collection,
        'filter': {},
        'sort': [('_id', 1)],
        'limit': 5,
    }

    # gets the first page
    cursor1 = get_keyset_cursor(**search_condictions)
    print('page1:', list(cursor1))  # [{'_id': 0}, {'_id': 1}, {'_id': 2}, {'_id': 3}, {'_id': 4}]

    # gets the second page
    cursor2 = get_keyset_cursor(**search_condictions, position=cursor1.paging.next_position)
    print('page2:', list(cursor2))  # [{'_id': 5}, {'_id': 6}]

    collection.insert({'_id': -1})

    # the first page again, backwards from the previous page
    cursor1 = get_keyset_cursor(**search_condictions, position=cursor2.paging.previous_position)
    print('page1:', list(cursor1))  # [{'_id': 0}, {'_id': 1}, {'_id': 2}, {'_id': 3}, {'_id': 4}]

    # what if new items were added at the start?
    if cursor1.paging.has_previous:
        cursor0 = get_keyset_cursor(**search_condictions, position=cursor1.paging.previous_position)
        print('page0:', list(cursor0))  # [{'_id': -1}]

Install
-----------

Install by pypi (not available for now)
###########

.. code-block:: shell

    pip3 install pymongokeyset

Install by source code
###########

.. code-block:: shell

    python3 setup.py sdist
    pip3 install ./dist/pymongokeyset-0.1.3.tar
