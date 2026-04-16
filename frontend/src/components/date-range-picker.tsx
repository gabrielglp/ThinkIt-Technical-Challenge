"use client";

import { useState } from "react";
import {
  addMonths,
  differenceInCalendarDays,
  eachDayOfInterval,
  endOfMonth,
  endOfWeek,
  format,
  isSameDay,
  isSameMonth,
  isWithinInterval,
  parseISO,
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

interface DateRangePickerProps {
  startDate?: string;
  endDate?: string;
  onChange: (start: string | undefined, end: string | undefined) => void;
  placeholder?: string;
}

export function DateRangePicker({
  startDate,
  endDate,
  onChange,
  placeholder = "Selecionar período",
}: DateRangePickerProps) {
  const [open, setOpen] = useState(false);
  const [viewMonth, setViewMonth] = useState(new Date());
  const [tempStart, setTempStart] = useState<Date | null>(
    startDate ? parseISO(startDate) : null
  );
  const [tempEnd, setTempEnd] = useState<Date | null>(
    endDate ? parseISO(endDate) : null
  );
  const [hoverDate, setHoverDate] = useState<Date | null>(null);

  const days = eachDayOfInterval({
    start: startOfWeek(startOfMonth(viewMonth), { weekStartsOn: 1 }),
    end: endOfWeek(endOfMonth(viewMonth), { weekStartsOn: 1 }),
  });

  const selectedCount =
    tempStart && tempEnd
      ? differenceInCalendarDays(tempEnd, tempStart) + 1
      : tempStart
      ? 1
      : 0;

  function handleDayClick(day: Date) {
    if (!tempStart || (tempStart && tempEnd)) {
      setTempStart(day);
      setTempEnd(null);
    } else {
      if (day < tempStart) {
        setTempEnd(tempStart);
        setTempStart(day);
      } else if (isSameDay(day, tempStart)) {
        setTempStart(null);
      } else {
        setTempEnd(day);
      }
    }
  }

  function isInRange(day: Date): boolean {
    const end = tempEnd ?? hoverDate;
    if (!tempStart || !end) return false;
    const [s, e] = tempStart <= end ? [tempStart, end] : [end, tempStart];
    return isWithinInterval(day, { start: s, end: e });
  }

  function isRangeStart(day: Date): boolean {
    const end = tempEnd ?? hoverDate;
    if (!tempStart) return false;
    if (!end || tempStart <= end) return isSameDay(day, tempStart);
    return isSameDay(day, end);
  }

  function isRangeEnd(day: Date): boolean {
    const end = tempEnd ?? hoverDate;
    if (!tempStart || !end) return false;
    if (tempStart <= end) return isSameDay(day, end);
    return isSameDay(day, tempStart);
  }

  function handleApply() {
    onChange(
      tempStart ? format(tempStart, "yyyy-MM-dd") : undefined,
      tempEnd ? format(tempEnd, "yyyy-MM-dd") : undefined
    );
    setOpen(false);
  }

  function handleClear() {
    setTempStart(null);
    setTempEnd(null);
  }

  function handleOpenChange(value: boolean) {
    if (value) {
      setTempStart(startDate ? parseISO(startDate) : null);
      setTempEnd(endDate ? parseISO(endDate) : null);
      setViewMonth(startDate ? parseISO(startDate) : new Date());
    }
    setOpen(value);
  }

  const triggerLabel =
    startDate && endDate
      ? `${format(parseISO(startDate), "dd/MM/yyyy")} – ${format(parseISO(endDate), "dd/MM/yyyy")}`
      : startDate
      ? `${format(parseISO(startDate), "dd/MM/yyyy")} – ...`
      : placeholder;

  return (
    <Popover open={open} onOpenChange={handleOpenChange}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          className={cn(
            "w-[240px] justify-start gap-2 font-normal",
            !startDate && !endDate && "text-muted-foreground"
          )}
        >
          <CalendarIcon className="h-4 w-4 shrink-0" />
          <span className="truncate">{triggerLabel}</span>
          {(startDate || endDate) && (
            <X
              className="h-3 w-3 ml-auto shrink-0 opacity-50 hover:opacity-100"
              onClick={(e) => {
                e.stopPropagation();
                onChange(undefined, undefined);
              }}
            />
          )}
        </Button>
      </PopoverTrigger>

      <PopoverContent className="w-auto p-0 select-none">
        {selectedCount > 0 && (
          <div className="flex justify-center py-2 px-3 bg-emerald-700 text-white text-xs font-medium rounded-t-md">
            {selectedCount} dia{selectedCount !== 1 ? "(s)" : ""} selecionado{selectedCount !== 1 ? "(s)" : ""}
          </div>
        )}

        <div className="p-3">
          <div className="flex items-center justify-between mb-3">
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              onClick={() => setViewMonth(subMonths(viewMonth, 1))}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>

            <span className="text-sm font-semibold capitalize">
              {format(viewMonth, "MMMM 'de' yyyy", { locale: ptBR })}
            </span>

            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              onClick={() => setViewMonth(addMonths(viewMonth, 1))}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>

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
              const inRange = isInRange(day);
              const rangeStart = isRangeStart(day);
              const rangeEnd = isRangeEnd(day);
              const isCurrentMonth = isSameMonth(day, viewMonth);
              const isSelected = rangeStart || rangeEnd;

              return (
                <div
                  key={i}
                  className={cn(
                    "h-8 flex items-center justify-center text-xs cursor-pointer relative",
                    inRange && !isSelected && "bg-emerald-700",
                    rangeStart && "rounded-l-full",
                    rangeEnd && "rounded-r-full",
                    !inRange && "rounded-full",
                    !isCurrentMonth && "opacity-30"
                  )}
                  onClick={() => handleDayClick(day)}
                  onMouseEnter={() => tempStart && !tempEnd && setHoverDate(day)}
                  onMouseLeave={() => setHoverDate(null)}
                >
                  <span
                    className={cn(
                      "h-7 w-7 flex items-center justify-center rounded-full transition-colors",
                      isSelected
                        ? "bg-emerald-700 text-white font-semibold"
                        : inRange
                        ? "text-white hover:bg-emerald-600"
                        : "hover:bg-muted"
                    )}
                  >
                    {format(day, "d")}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="flex items-center justify-end gap-2 px-3 pb-3">
          <Button variant="outline" size="sm" onClick={handleClear}>
            Limpar
          </Button>
          <Button
            size="sm"
            className="bg-emerald-700 hover:bg-emerald-800 text-white"
            onClick={handleApply}
          >
            Aplicar
          </Button>
        </div>
      </PopoverContent>
    </Popover>
  );
}
