import { useState } from "react";
import {
  Box,
  Package,
  PackageOpen,
  ShieldCheck,
  RotateCcw,
} from "lucide-react";

import LockerScene from "../components/locker/LockerScene";
import { useLockerStore } from "../stores/lockerStore";

export default function HomePage() {
  const {
    lockers,
    selectedLocker,
    allocateLocker,
    openLocker,
    closeLocker,
    completeDeposit,
    cancelReservation,
    retrieveLocker,
  } = useLockerStore();

  const [message, setMessage] = useState("Chào mừng đến với Smart Face Locker");

  const available = lockers.filter(
    (locker) => locker.status === "AVAILABLE",
  ).length;

  const occupied = lockers.filter(
    (locker) => locker.status === "OCCUPIED",
  ).length;

  const selected = lockers.find((locker) => locker.id === selectedLocker);

  const handleDeposit = () => {
    if (selectedLocker !== null) {
      setMessage("Vui lòng hoàn thành phiên gửi đồ hiện tại.");
      return;
    }

    const id = allocateLocker();

    if (id === null) {
      setMessage("Hiện tại không còn tủ trống.");
      return;
    }

    setMessage(`Đã phân bổ tủ ${String(id).padStart(3, "0")}.`);
  };

  const handleOpen = () => {
    if (!selected) return;

    openLocker(selected.id);
    setMessage(`Đã mở tủ ${selected.number}.`);
  };

  const handleClose = () => {
    if (!selected) return;

    closeLocker(selected.id);
    setMessage(`Đã đóng tủ ${selected.number}.`);
  };

  const handleComplete = () => {
    if (!selected || selected.doorStatus !== "CLOSED") return;

    completeDeposit(selected.id);
    setMessage(`Gửi đồ thành công tại tủ ${selected.number}.`);
  };

  const handleRetrieve = () => {
    const locker = lockers.find(
      (item) => item.status === "OCCUPIED" && item.doorStatus === "CLOSED",
    );

    if (!locker) {
      setMessage("Không có phiên gửi đồ nào để mô phỏng lấy đồ.");
      return;
    }

    // Chỉ dùng để kiểm thử giao diện.
    // Phiên bản thật phải xác thực khuôn mặt trước khi mở.
    retrieveLocker(locker.id);

    setMessage(`Đã mô phỏng lấy đồ từ tủ ${locker.number}.`);
  };

  return (
    <div className="min-h-screen bg-slate-100">
      {/* HEADER */}
      <header className="bg-[#101b35] px-8 py-5 text-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-blue-600 p-3">
              <Box size={26} />
            </div>

            <div>
              <h1 className="text-2xl font-bold">Smart Face Locker</h1>
              <p className="text-sm text-slate-300">
                Hệ thống gửi đồ thông minh bằng AI
              </p>
            </div>
          </div>

          <div className="rounded-full bg-blue-500/20 px-5 py-2 text-sm">
            ● Simulation Mode
          </div>
        </div>
      </header>

      {/* MAIN */}
      <main className="mx-auto grid max-w-7xl gap-6 p-6 lg:grid-cols-[1fr_350px]">
        {/* 3D SCENE */}
        <section className="overflow-hidden rounded-3xl bg-white shadow-xl">
          <div className="flex items-center justify-between border-b p-5">
            <div>
              <h2 className="text-xl font-bold text-slate-900">
                Hệ thống tủ thông minh
              </h2>
              <p className="text-sm text-slate-500">Mô hình 3D tương tác</p>
            </div>

            <span className="rounded-full bg-green-100 px-4 py-2 text-sm font-medium text-green-700">
              ● Online
            </span>
          </div>

          <div className="h-[560px]">
            <LockerScene />
          </div>

          <div className="border-t px-5 py-4 text-sm text-slate-500">
            Kéo chuột để xoay • Cuộn để phóng to hoặc thu nhỏ
          </div>
        </section>

        {/* CONTROL PANEL */}
        <aside className="space-y-5">
          <div className="rounded-3xl bg-white p-6 shadow-lg">
            <div className="mb-5 flex justify-center">
              <div className="rounded-full bg-blue-100 p-5 text-blue-600">
                <ShieldCheck size={42} />
              </div>
            </div>

            <h2 className="text-center text-2xl font-bold text-slate-900">
              Smart Face Locker
            </h2>

            <p className="mt-3 text-center text-sm text-slate-500">
              Gửi và lấy đồ nhanh chóng, an toàn bằng công nghệ nhận diện khuôn
              mặt.
            </p>

            <div className="mt-8 space-y-3">
              <button
                onClick={handleDeposit}
                className="flex w-full items-center justify-center gap-3 rounded-xl bg-blue-600 px-6 py-4 font-semibold text-white transition hover:bg-blue-700"
              >
                <Package size={22} />
                Gửi đồ
              </button>

              <button
                onClick={handleRetrieve}
                className="flex w-full items-center justify-center gap-3 rounded-xl border border-slate-200 px-6 py-4 font-semibold text-slate-900 transition hover:bg-slate-100"
              >
                <PackageOpen size={22} />
                Lấy đồ (Demo)
              </button>
            </div>
          </div>

          {/* LOCKER STATUS */}
          <div className="rounded-3xl bg-white p-6 shadow-lg">
            <h3 className="mb-5 text-lg font-bold">Trạng thái tủ</h3>

            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-xl bg-green-50 p-4">
                <p className="text-sm text-green-700">Còn trống</p>
                <p className="text-3xl font-bold text-green-600">{available}</p>
              </div>

              <div className="rounded-xl bg-red-50 p-4">
                <p className="text-sm text-red-700">Đang sử dụng</p>
                <p className="text-3xl font-bold text-red-600">{occupied}</p>
              </div>
            </div>

            <p className="mt-4 text-sm text-slate-500">
              Tổng số: {lockers.length} tủ
            </p>
          </div>

          {/* SIMULATION CONTROL */}
          {selected && (
            <div className="rounded-3xl bg-white p-6 shadow-lg">
              <h3 className="text-lg font-bold">Tủ số {selected.number}</h3>

              <p className="mt-2 text-sm text-slate-500">
                Trạng thái: {selected.status}
              </p>

              <div className="mt-5 space-y-3">
                {selected.doorStatus === "CLOSED" ? (
                  <button
                    onClick={handleOpen}
                    className="w-full rounded-xl bg-blue-600 p-3 font-semibold text-white"
                  >
                    Mở cửa tủ
                  </button>
                ) : (
                  <button
                    onClick={handleClose}
                    className="w-full rounded-xl bg-amber-500 p-3 font-semibold text-white"
                  >
                    Đóng cửa tủ
                  </button>
                )}

                <button
                  onClick={handleComplete}
                  disabled={selected.doorStatus === "OPEN"}
                  className="w-full rounded-xl bg-green-600 p-3 font-semibold text-white disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Xác nhận gửi đồ
                </button>

                <button
                  onClick={() => {
                    cancelReservation(selected.id);
                    setMessage("Đã hủy giữ chỗ.");
                  }}
                  disabled={selected.doorStatus === "OPEN"}
                  className="flex w-full items-center justify-center gap-2 rounded-xl border p-3 disabled:opacity-40"
                >
                  <RotateCcw size={18} />
                  Hủy
                </button>
              </div>
            </div>
          )}

          {/* NOTIFICATION */}
          <div className="rounded-2xl bg-blue-50 p-5 text-sm font-medium text-blue-800">
            {message}
          </div>
        </aside>
      </main>
    </div>
  );
}
