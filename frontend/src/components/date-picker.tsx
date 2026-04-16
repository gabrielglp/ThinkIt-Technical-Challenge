"use client";

import { useState } from "react";
import {
  addMonths,
  eachDayOfInterval,
  endOfMonth,
  endOfWeek,
  format,
  isSameDay,
  isSameMonth,
  parseISO,
  setYear,
  startOfMonth,
  startOfWeek,
  subMonths,
} from "date-fns";
import { ptBR } from "date-fns/locale";
import { CalendarIcon, ChevronLeft, ChevronRight, X } from "lucide-react";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const WEEKDAYS = ["S", "T", "Q", "Q", "S", "S", "D"];

interface DatePickerProps {
  value?: string; // yyyy-MM-dd
  onChange: (value: string | undefined) => void;
  placeholder?: string;
  className?: string;
}

export function DatePicker({
  value,
  onChange,
  placeholder = "Selecionar data",
  className,
}: DatePickerProps) {
  const [open, setOpen] = useState(false);
  const [view, setView] = useState<"calendar" | "year">("calendar");
  const [viewMonth, setViewMonth] = useState(value ? parseISO(value) : new Date());
  const [yearPage, setYearPage] = useState(0);

  const currentYear = viewMonth.getFullYear();
  const years = Array.from({ length: 12 }, (_, i) => currentYear - 5 + yearPage * 12 + i);

  const days = eachDayOfInterval({
    start: startOfWeek(startOfMonth(viewMonth), { weekStartsOn: 1 }),
    end: endOfWeek(endOfMonth(viewMonth), { weekStartsOn: 1 }),
  });

  function handleDayClick(day: Date) {
    onChange(format(day, "yyyy-MM-dd"));
    setOpen(false);
  }

  function handleOpenChange(next: boolean) {
    if (next) {
      setViewMonth(value ? parseISO(value) : new Date());
      setView("calendar");
      setYearPage(0);
    }
    setOpen(next);
  }

  function handleYearSelect(year: number) {
    setViewMonth(setYear(viewMonth, year));
    setView("calendar");
  }

  const triggerLabel = value
    ? format(parseISO(value), "dd/MM/yyyy")
    : placeholder;

  return (
    <Popover open={open} onOpenChange={handleOpenChange}>
      <PopoverTrigger asChild>
        <Button
          type="button"
          variant="outline"
          className={cn(
            "w-full justify-start gap-2 font-normal",
            !value && "text-muted-foreground",
            className
          )}
        >
          <CalendarIcon className="h-4 w-4 shrink-0" />
          <span className="truncate">{triggerLabel}</span>
          {value && (
            <X
              className="h-3 w-3 ml-auto shrink-0 opacity-50 hover:opacity-100"
              onClick={(e) => {
                e.stopPropagation();
                onChange(undefined);
              }}
            />
          )}
        </Button>
      </PopoverTrigger>

      <PopoverContent className="w-auto p-0 select-none">
        <div className="p-3 w-[238px]">
          {/* Header */}
          <div className="flex items-center justify-between mb-3">
            {view === "calendar" && (
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="h-7 w-7"
                onClick={() => setViewMonth(subMonths(viewMonth, 1))}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
            )}

            <button
              type="button"
              className="text-sm font-semibold capitalize hover:text-emerald-600 transition-colors cursor-pointer mx-auto"
              onClick={() => { setView(view === "year" ? "calendar" : "year"); setYearPage(0); }}
            >
              {format(viewMonth, "MMMM 'de' yyyy", { locale: ptBR })}
            </button>

            {view === "calendar" && (
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="h-7 w-7"
                onClick={() => setViewMonth(addMonths(viewMonth, 1))}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            )}
          </div>

          {/* Year grid */}
          {view === "year" && (
            <>
              <div className="flex items-center justify-between mb-2">
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7"
                  onClick={() => setYearPage((p) => p - 1)}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <span className="text-xs text-muted-foreground font-medium">
                  {years[0]} – {years[years.length - 1]}
                </span>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7"
                  onClick={() => setYearPage((p) => p + 1)}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
              <div className="grid grid-cols-4 gap-1">
                {years.map((year) => (
                  <button
                    type="button"
                    key={year}
                    onClick={() => handleYearSelect(year)}
                    className={cn(
                      "w-full h-9 rounded-md text-sm font-medium transition-colors hover:bg-muted",
                      year === currentYear && "bg-emerald-700 text-white hover:bg-emerald-800"
                    )}
                  >
                    {year}
                  </button>
                ))}
              </div>
            </>
          )}

          {/* Calendar grid */}
          {view === "calendar" && (
            <>
              <div className="grid grid-cols-7 mb-1">
                {WEEKDAYS.map((d, i) => (
                  <div
                    key={i}
                    className="h-8 flex items-center justify-center text-xs font-medium text-muted-foreground"
                  >
                    {d}
                  </div>
                ))}
              </div>

              <div className="grid grid-cols-7">
                {days.map((day, i) => {
                  const selected = value ? isSameDay(day, parseISO(value)) : false;
                  const isCurrentMonth = isSameMonth(day, viewMonth);

                  return (
                    <div
                      key={i}
                      className={cn(
                        "h-8 flex items-center justify-center text-xs cursor-pointer rounded-full",
                        !isCurrentMonth && "opacity-30"
                      )}
                      onClick={() => handleDayClick(day)}
                    >
                      <span
                        className={cn(
                          "h-7 w-7 flex items-center justify-center rounded-full transition-colors",
                          selected
                            ? "bg-emerald-700 text-white font-semibold"
                            : "hover:bg-muted"
                        )}
                      >
                        {format(day, "d")}
                      </span>
                    </div>
                  );
                })}
              </div>
            </>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
}
