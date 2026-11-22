export type LockerStatus =
  | "AVAILABLE"
  | "RESERVED"
  | "OCCUPIED"
  | "MAINTENANCE";

export type DoorStatus = "OPEN" | "CLOSED";

export interface Locker {
  id: number;
  number: string;
  status: LockerStatus;
  doorStatus: DoorStatus;
}
