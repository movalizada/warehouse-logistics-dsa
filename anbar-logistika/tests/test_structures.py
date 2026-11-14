"""Bütün data strukturları və anbar xidməti üçün vahid testlər.

İşə salmaq:  python -m unittest discover -s tests -v
"""

import random
import unittest

from src.services.warehouse import Warehouse, WarehouseError
from src.structures.arrays import ArrayOverflowError, DynamicArray, StaticArray
from src.structures.bst import BinarySearchTree
from src.structures.hash_table import HashTable
from src.structures.linear_adts import Deque, EmptyStructureError, Queue, Stack
from src.structures.linked_lists import DoublyLinkedList, SinglyLinkedList


def as_tuple(iterable):
    return tuple(iterable)


class ArrayTests(unittest.TestCase):
    def test_static_overflow(self):
        arr = StaticArray(3)
        for i in range(3):
            arr.append(i)
        with self.assertRaises(ArrayOverflowError):
            arr.append(99)
        with self.assertRaises(ArrayOverflowError):
            arr.insert(0, 99)

    def test_dynamic_doubling(self):
        arr = DynamicArray()
        capacities = DynamicArray()
        for i in range(17):
            arr.append(i)
            capacities.append(arr.capacity)
        self.assertEqual(arr.capacity, 32)
        self.assertEqual(arr.resize_count, 5)  # 1→2→4→8→16→32
        self.assertEqual(as_tuple(arr), tuple(range(17)))

    def test_insert_delete_search(self):
        for arr in (StaticArray(10), DynamicArray()):
            for v in (1, 2, 3):
                arr.append(v)
            arr.insert(0, 0)
            arr.insert(2, 99)
            self.assertEqual(as_tuple(arr), (0, 1, 99, 2, 3))
            self.assertEqual(arr.delete(2), 99)
            self.assertEqual(arr.pop(), 3)
            self.assertEqual(arr.search(2), 2)
            self.assertEqual(arr.search(42), -1)
            with self.assertRaises(IndexError):
                arr.get(10)


class LinkedListTests(unittest.TestCase):
    def test_both_lists(self):
        for cls in (SinglyLinkedList, DoublyLinkedList):
            lst = cls()
            lst.push_back(2)
            lst.push_back(3)
            lst.push_front(1)
            self.assertEqual(as_tuple(lst), (1, 2, 3))
            self.assertEqual(as_tuple(lst.traverse_backward()), (3, 2, 1))
            self.assertEqual(lst.pop_back(), 3)
            self.assertEqual(lst.pop_front(), 1)
            self.assertEqual(lst.pop_back(), 2)
            self.assertTrue(lst.is_empty())
            self.assertIsNone(lst.tail)
            with self.assertRaises(EmptyStructureError):
                lst.pop_front()

    def test_singly_insert_and_remove(self):
        lst = SinglyLinkedList()
        for v in (1, 3, 4):
            lst.push_back(v)
        lst.insert_at(1, 2)
        self.assertEqual(as_tuple(lst), (1, 2, 3, 4))
        self.assertEqual(lst.remove_where(lambda x: x == 4), 4)
        lst.push_back(5)  # tail düzgün yenilənməlidir
        self.assertEqual(as_tuple(lst), (1, 2, 3, 5))

    def test_doubly_remove_node(self):
        lst = DoublyLinkedList()
        nodes = DynamicArray()
        for v in range(5):
            nodes.append(lst.push_back(v))
        lst.remove_node(nodes[2])
        lst.remove_node(nodes[0])
        lst.remove_node(nodes[4])
        self.assertEqual(as_tuple(lst), (1, 3))
        self.assertEqual(as_tuple(lst.traverse_backward()), (3, 1))

    def test_node_memory(self):
        self.assertGreater(DoublyLinkedList.node_size_bytes(), SinglyLinkedList.node_size_bytes())


class LinearADTTests(unittest.TestCase):
    def test_stack(self):
        s = Stack()
        for v in (1, 2, 3):
            s.push(v)
        self.assertEqual(s.peek(), 3)
        self.assertEqual((s.pop(), s.pop(), s.pop()), (3, 2, 1))
        with self.assertRaises(EmptyStructureError):
            s.pop()

    def test_queue(self):
        q = Queue()
        for v in (1, 2, 3):
            q.enqueue(v)
        self.assertEqual((q.dequeue(), q.dequeue()), (1, 2))
        q.enqueue(4)
        self.assertEqual(as_tuple(q), (3, 4))
        self.assertEqual(len(q), 2)

    def test_deque(self):
        d = Deque()
        d.add_rear(2)
        d.add_front(1)
        d.add_rear(3)
        d.add_front(0)
        self.assertEqual(as_tuple(d), (0, 1, 2, 3))
        self.assertEqual(d.remove_where(lambda x: x == 2), 2)
        self.assertEqual(d.remove_rear(), 3)
        self.assertEqual(d.remove_front(), 0)
        self.assertEqual(as_tuple(d), (1,))
        self.assertIsNone(d.remove_where(lambda x: x == 42))


class HashTableTests(unittest.TestCase):
    def test_put_get_remove_and_rehash(self):
        t = HashTable(capacity=4)
        for i in range(100):
            t.put("SKU-{0}".format(i), i)
        self.assertEqual(len(t), 100)
        self.assertGreater(t.bucket_count, 4)
        self.assertLessEqual(t.load_factor(), 0.75)
        for i in range(100):
            self.assertEqual(t.get("SKU-{0}".format(i)), i)
        self.assertFalse(t.put("SKU-5", 500))
        self.assertEqual(t.get("SKU-5"), 500)
        self.assertEqual(t.remove("SKU-5"), 500)
        self.assertIsNone(t.get("SKU-5"))
        with self.assertRaises(KeyError):
            t.remove("SKU-5")

    def test_collisions_with_fixed_buckets(self):
        t = HashTable(capacity=5, auto_resize=False)
        for i in range(20):
            t.put(i, i)
        st = t.stats()
        self.assertEqual(st.total_items, 20)
        self.assertEqual(st.collisions, 20 - (5 - st.empty_buckets))
        self.assertGreaterEqual(st.longest_chain, 4)
        self.assertAlmostEqual(st.load_factor, 4.0)


class BSTTests(unittest.TestCase):
    def build(self, keys):
        tree = BinarySearchTree()
        for k in keys:
            tree.insert(k, str(k))
        return tree

    def test_insert_search_inorder(self):
        tree = self.build((50, 30, 70, 20, 40, 60, 80))
        self.assertEqual(tuple(k for k, _ in tree.in_order()), (20, 30, 40, 50, 60, 70, 80))
        self.assertEqual(tree.search(60), "60")
        self.assertIsNone(tree.search(65))
        self.assertEqual(tree.get_height(), 3)

    def test_delete_three_cases(self):
        tree = self.build((50, 30, 70, 20, 40, 60, 80, 65))
        self.assertTrue(tree.delete(20))   # yarpaq
        self.assertTrue(tree.delete(60))   # bir uşaq (65)
        self.assertTrue(tree.delete(50))   # iki uşaq — kök, varis 65
        self.assertFalse(tree.delete(999))
        self.assertEqual(tree.root.key, 65)
        self.assertEqual(tuple(k for k, _ in tree.in_order()), (30, 40, 65, 70, 80))
        self.assertEqual(len(tree), 5)

    def test_random_delete_consistency(self):
        rng = random.Random(7)
        keys = DynamicArray()
        for i in range(500):
            keys.append(i)
        for i in range(499, 0, -1):
            j = rng.randint(0, i)
            keys[i], keys[j] = keys[j], keys[i]
        tree = self.build(keys)
        for i in range(0, 500, 2):
            self.assertTrue(tree.delete(i))
        self.assertEqual(tuple(k for k, _ in tree.in_order()), tuple(range(1, 500, 2)))

    def test_range_query(self):
        tree = self.build(range(1, 101))
        self.assertEqual(tuple(k for k, _ in tree.range_query(10, 15)), (10, 11, 12, 13, 14, 15))
        self.assertEqual(tuple(tree.range_query(200, 300)), ())

    def test_sorted_input_degenerates(self):
        tree = self.build(range(2000))  # iterativ olduğu üçün rekursiya limiti problemi yoxdur
        self.assertEqual(tree.get_height(), 2000)


class WarehouseTests(unittest.TestCase):
    def setUp(self):
        self.wh = Warehouse()
        self.wh.seed_sample_data()

    def test_seed(self):
        self.assertEqual(len(self.wh.catalog), 20)
        self.assertEqual(len(self.wh.sku_index), 20)
        self.assertEqual(len(self.wh.price_index), 20)
        self.assertTrue(self.wh.undo_stack.is_empty())

    def test_add_update_delete_undo(self):
        wh = self.wh
        wh.add_product("tst-1", "Test", 10, 5)
        wh.update_product("TST-1", price=12.5, quantity=7)
        wh.remove_product("TST-1")
        self.assertIsNone(wh.get_product("TST-1"))
        wh.undo()  # silməni geri qaytar
        self.assertEqual(wh.get_product("TST-1").price, 12.5)
        wh.undo()  # yeniləməni geri qaytar
        p = wh.get_product("TST-1")
        self.assertEqual((p.price, p.quantity), (10.0, 5))
        self.assertTrue(wh.price_index.contains((10.0, "TST-1")))
        self.assertFalse(wh.price_index.contains((12.5, "TST-1")))
        wh.undo()  # əlavəni geri qaytar
        self.assertIsNone(wh.get_product("TST-1"))
        self.assertEqual(len(wh.catalog), 20)
        with self.assertRaises(WarehouseError):
            wh.undo()

    def test_orders_flow(self):
        wh = self.wh
        vip = wh.create_order("VIP müştəri", "ELK-1003", 5, vip=True)
        self.assertIs(wh.dispatch_line.peek_front(), vip)
        before = wh.get_product("ELK-1003").quantity
        order, ok = wh.dispatch_next()
        self.assertTrue(ok)
        self.assertEqual(wh.get_product("ELK-1003").quantity, before - 5)
        wh.undo()
        self.assertEqual(wh.get_product("ELK-1003").quantity, before)
        big = wh.create_order("X", "GEY-6002", 999, vip=True)
        order, ok = wh.dispatch_next()
        self.assertIs(order, big)
        self.assertFalse(ok)

    def test_range_reports(self):
        cheap = tuple(p.sku for p in self.wh.products_in_price_range(0, 10))
        self.assertEqual(cheap, ("MƏT-3002", "TİK-4001"))
        low = tuple(p.quantity for p in self.wh.products_in_stock_range(0, 10))
        self.assertEqual(low, (3, 5, 7, 9))

    def test_shelves_and_docks(self):
        wh = self.wh
        self.assertEqual(wh.current_shelf().code, "A-01")
        wh.move_forward()
        wh.move_forward()
        self.assertEqual(wh.move_backward().code, "A-02")
        wh.remove_current_shelf()
        self.assertEqual(wh.current_shelf().code, "B-01")
        with self.assertRaises(WarehouseError):
            wh.go_first_shelf() and wh.move_backward()
        for plate in ("A", "B", "C", "D"):
            wh.dock_truck(plate)
        with self.assertRaises(WarehouseError):
            wh.dock_truck("E")


if __name__ == "__main__":
    unittest.main()
