
// #generic

// this is not the type safe way
// function firstElement(arr: any[]): any {
//   return arr[0];
// }

// console.log(firstElement([0, 1]));

//////////////////////////////

// function firstElenemt<T>(arr: T[]): T {
//   return arr[0];
// }

// console.log(firstElenemt([0, 1]));

//////////////////////////////

// #constraint
// can limit what types are allowed

// function logLength<T extends { length: number }>(item: T): number {
//   console.log(item.length);
//   return item.length;
// }

// logLength("hiiii");
// logLength([1,2]);
// logLength(123); // has lint error

//////////////////////////////

// ============================================================
// GENERIC FUNCTIONS
// ============================================================

// A generic function captures T at call time.
// Each call can infer a different T.
function identity<T>(value: T): T {
  return value;
}

const a = identity(42);       // T = number
const b = identity("hello");  // T = string
const c = identity(true);     // T = boolean

// Multiple type parameters
function pair<T, U>(first: T, second: U): [T, U] {
  return [first, second];
}

const p = pair("age", 30);    // [string, number]

// Generic arrow function (slightly different syntax)
const wrap = <T>(value: T): { data: T } => ({ data: value });

// ============================================================
// GENERIC INTERFACES
// ============================================================

// An interface with a type parameter — the type is set
// when you declare a variable / use the interface.
interface Box<T> {
  value: T;
  label: string;
}

const numberBox: Box<number> = { value: 42, label: "answer" };
const stringBox: Box<string> = { value: "hello", label: "greeting" };

// Generic interface with a function type
interface Mapper<T, U> {
  (item: T): U;
}

const toStr: Mapper<number, string> = (n) => n.toFixed(2);

// Interface with constraints
interface HasLength {
  length: number;
}

interface Container<T extends HasLength> {
  data: T;
  logLength(): number;
}

// ============================================================
// GENERIC CLASSES
// ============================================================

// A generic class fixes T when you instantiate it.
class Queue<T> {
  private items: T[] = [];

  enqueue(item: T): void {
    this.items.push(item);
  }

  dequeue(): T | undefined {
    return this.items.shift();
  }

  get size(): number {
    return this.items.length;
  }
}

const numberQueue = new Queue<number>();
numberQueue.enqueue(1);
numberQueue.enqueue(2);
const first = numberQueue.dequeue();  // T = number

const stringQueue = new Queue<string>();
stringQueue.enqueue("a");
// stringQueue.enqueue(1);  // ❌ Error: number not assignable to string

// Class with constrained type parameter
class ComparableBox<T extends { valueOf(): number }> {
  constructor(public value: T) {}

  isGreaterThan(other: T): boolean {
    return this.value.valueOf() > other.valueOf();
  }
}

// ============================================================
// KEY DIFFERENCES SUMMARY
// ============================================================
//
//                  When is T decided?     What does it describe?
//   ─────────────────────────────────────────────────────────────
//   Function       At CALL time           A single operation
//   Interface      At USE/IMPLEMENT time  A contract / shape
//   Class          At INSTANTIATION time  An object with state + behavior
