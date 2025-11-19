class DLNode:
    def __init__(self, value):
        self.data = value
        self.left = None
        self.right = None

    def insertright(self, value):
        p = self
        q = DLNode(value)
        r = p.right

        q.right = r
        q.left = p
        p.right = q

        if r is not None:
            r.left = q
    
    def insertleft(self, value):
        r = self
        q = DLNode(value)
        p = r.left

        r.left = q
        q.right = r
        q.left = p
        if p is not None:
            p.right = q

    def delete(self):
        p = self.left
        q = self
        r = self.right

        if p is not None:
            p.right = r
        
        if r is not None:
            r.left = p
        
        if p is None:
            return r, q
        
        return p, q

    def traverse(self):
        a = self

        while a.left is not None:
            a = a.left
        
        print("Traversing Doubly Linked List:")
        while a is not None:
            print(a.data, end="")
            if a.right is not None:
                print(" <-> ", end="")
            a = a.right
        print()
    
    def __len__(self):
        a = self
        i = 0
        while a is not None:
            i += 1
            a = a.left

        b = self.right
        while b is not None:
            i += 1
            b = b.right

        return i
    
    def search(self, target):
        a = self
        if a.data == target:
            return a
        
        while a is not None and a.data != target:
            a = a.right
        
        if a is not None:
            return a
        
        a = self.left

        while a is not None and a.data != target:
            a = a.left
        
        return a
        

def buildlistright(value):
    node = DLNode(value[0])
    for i in range(1, len(value)):
        node.insertright(value[i])
        node = node.right
    
    return node

def buildlistleft(value):
    node = DLNode(value[0])
    for i in range(1, len(value)):
        node.insertleft(value[i])
        node = node.left
    
    return node


# print("=== TEST 1: Build list using insertright ===")
# head = buildlistright([10, 20, 30, 40])
# head.traverse()  # should show 10 <-> 20 <-> 30 <-> 40 <-> None
# print("Length:", len(head))  # should be 4


# print("\n=== TEST 2: Build list using insertleft ===")
# head2 = buildlistleft([10, 20, 30, 40])
# head2.traverse()  # should show 40 <-> 30 <-> 20 <-> 10 <-> None
# print("Length:", len(head2))  # should be 4


# print("\n=== TEST 3: Insert at left and right of middle node ===")
# mid = head.search(20)
# mid.insertright(25)
# mid.insertleft(15)
# head.traverse()  # expected: 10 <-> 15 <-> 20 <-> 25 <-> 30 <-> 40 <-> None
# print("Length after inserts:", len(head))


# print("\n=== TEST 4: Delete a node ===")
# target = head.search(25)
# head, deleted = target.delete()
# print(f"Deleted node: {deleted.data}")
# head.traverse()  # expected: 10 <-> 15 <-> 20 <-> 30 <-> 40 <-> None
# print("Length after delete:", len(head))


# print("\n=== TEST 5: Delete head node ===")
# target = head.search(10)
# head, deleted = target.delete()
# print(f"Deleted node: {deleted.data}")
# head.traverse()  # expected: 15 <-> 20 <-> 30 <-> 40 <-> None


# print("\n=== TEST 6: Search existing and non-existing values ===")
# node = head.search(30)
# print("Found:", node.data if node else "Not found")  # expected 30
# node = head.search(100)
# print("Found:", node.data if node else "Not found")  # expected Not found
