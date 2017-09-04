pymongokeyset
==================

Example
-----------

An executable example can be found at ``pymongokeyset/example/simple_examle.py``

.. code-block:: python
    collection = prepare()

    # gets the first page
    page1 = get_page(collection.find({}).sort([('_id', 1)]), limit=5)
    print('page1:', page1)  # [{'_id': 0}, {'_id': 1}, {'_id': 2}, {'_id': 3}, {'_id': 4}]

    # gets the second page
    page2 = get_page(collection.find({}).sort([('_id', 1)]), limit=5, position=page1.paging.next_position)
    print('page2:', page2)  # [{'_id': 5}, {'_id': 6}]

    # the first page again, backwards from the previous page
    page1 = get_page(collection.find({}).sort([('_id', 1)]), limit=5, position=page2.paging.previous_position)
    print('page1:', page1)  # [{'_id': 0}, {'_id': 1}, {'_id': 2}, {'_id': 3}, {'_id': 4}]

    # what if new items were added at the start?
    if page1.paging.has_previous:
        page0 = get_page(collection.find({}).sort([('_id', 1)]), limit=5, position=page1.paging.previous_position)
        print('page0:', page0)  # [{'_id': -1}]
