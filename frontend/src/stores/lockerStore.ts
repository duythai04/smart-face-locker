import { create } from "zustand";
import type { Locker } from "../types/locker";

interface LockerStore {
  lockers: Locker[];
  selectedLocker: number | null;

  allocateLocker: () => number | null;
  openLocker: (id: number) => void;
  closeLocker: (id: number) => void;
  completeDeposit: (id: number) => void;
  cancelReservation: (id: number) => void;
  retrieveLocker: (id: number) => void;
}

const initialLockers: Locker[] = Array.from({ length: 12 }, (_, index) => ({
  id: index + 1,
  number: String(index + 1).padStart(3, "0"),
  status: "AVAILABLE",
  doorStatus: "CLOSED",
}));

export const useLockerStore = create<LockerStore>((set, get) => ({
  lockers: initialLockers,
  selectedLocker: null,

  allocateLocker: () => {
    const available = get().lockers.find(
      (locker) =>
        locker.status === "AVAILABLE" && locker.doorStatus === "CLOSED",
    );

    if (!available) return null;

    set((state) => ({
      selectedLocker: available.id,
      lockers: state.lockers.map((locker) =>
        locker.id === available.id ? { ...locker, status: "RESERVED" } : locker,
      ),
    }));

    return available.id;
  },

  openLocker: (id) => {
    set((state) => ({
      selectedLocker: id,
      lockers: state.lockers.map((locker) =>
        locker.id === id && locker.status === "RESERVED"
          ? { ...locker, doorStatus: "OPEN" }
          : locker,
      ),
    }));
  },

  closeLocker: (id) => {
    set((state) => ({
      lockers: state.lockers.map((locker) =>
        locker.id === id ? { ...locker, doorStatus: "CLOSED" } : locker,
      ),
    }));
  },

  completeDeposit: (id) => {
    set((state) => ({
      selectedLocker: null,
      lockers: state.lockers.map((locker) =>
        locker.id === id &&
        locker.status === "RESERVED" &&
        locker.doorStatus === "CLOSED"
          ? { ...locker, status: "OCCUPIED" }
          : locker,
      ),
    }));
  },

  cancelReservation: (id) => {
    set((state) => ({
      selectedLocker: null,
      lockers: state.lockers.map((locker) =>
        locker.id === id &&
        locker.status === "RESERVED" &&
        locker.doorStatus === "CLOSED"
          ? { ...locker, status: "AVAILABLE" }
          : locker,
      ),
    }));
  },

  retrieveLocker: (id) => {
    set((state) => ({
      selectedLocker: null,
      lockers: state.lockers.map((locker) =>
        locker.id === id &&
        locker.status === "OCCUPIED" &&
        locker.doorStatus === "CLOSED"
          ? { ...locker, status: "AVAILABLE" }
          : locker,
      ),
    }));
  },
}));
