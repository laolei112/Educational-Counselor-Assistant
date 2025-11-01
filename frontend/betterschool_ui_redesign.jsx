import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectTrigger, SelectContent, SelectItem } from "@/components/ui/select";
import { Sheet, SheetTrigger, SheetContent } from "@/components/ui/sheet";
import { Search, SlidersHorizontal } from "lucide-react";
import { motion } from "framer-motion";

export default function BetterSchoolRedesign() {
  const allSchools = [
    {
      name: "嘉诺撒圣心学校私立部",
      district: "中西区",
      type: "女校 · 私立 · 天主教",
      fee: 53680,
      secondary: "嘉诺撒圣心书院",
      band: 100,
    },
    {
      name: "九龙塘学校（小学部）",
      district: "九龙城区",
      type: "男女校 · 私立",
      fee: 69000,
      secondary: "-",
      band: 91.84,
    },
  ];

  const [filter, setFilter] = useState({ district: "all", type: "all", sort: "none" });
  const [search, setSearch] = useState("");

  // 动态筛选与排序逻辑
  const filteredSchools = allSchools
    .filter((s) =>
      filter.district === "all" ? true : s.district.includes(filter.district)
    )
    .filter((s) =>
      filter.type === "all" ? true : s.type.includes(filter.type)
    )
    .filter((s) => s.name.includes(search))
    .sort((a, b) => {
      if (filter.sort === "band") return b.band - a.band;
      if (filter.sort === "fee") return b.fee - a.fee;
      if (filter.sort === "district") return a.district.localeCompare(b.district);
      return 0;
    });

  return (
    <div className="min-h-screen bg-gray-50 text-gray-800">
      {/* Header Section */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-400 text-white py-10 px-6 text-center">
        <h1 className="text-3xl font-bold mb-3">BetterSchool · 香港小学升学数据库</h1>
        <p className="text-sm opacity-90">为您智能匹配最适合孩子的升学路径</p>
        <div className="max-w-xl mx-auto mt-6 flex bg-white rounded-full shadow-md overflow-hidden">
          <Search className="text-gray-400 w-5 h-5 m-3" />
          <Input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="搜索学校名称、地区、校网…"
            className="border-none focus-visible:ring-0 focus:outline-none text-gray-700"
          />
        </div>
      </div>

      {/* Filter + Sort Section */}
      <div className="bg-white shadow-sm py-4 px-4 md:px-10 flex flex-wrap items-center justify-between gap-3">
        <div className="flex gap-2 text-sm font-medium">
          <Button variant="secondary" className="rounded-full">小学</Button>
          <Button variant="ghost" className="rounded-full">初中</Button>
          <Button variant="ghost" className="rounded-full">高中</Button>
        </div>

        {/* Desktop Filters */}
        <div className="hidden md:flex gap-3 items-center flex-wrap">
          <Select onValueChange={(v) => setFilter({ ...filter, district: v })}>
            <SelectTrigger className="w-[120px]">区域</SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部</SelectItem>
              <SelectItem value="中西区">香港岛</SelectItem>
              <SelectItem value="九龙城区">九龙</SelectItem>
              <SelectItem value="新界">新界</SelectItem>
            </SelectContent>
          </Select>

          <Select onValueChange={(v) => setFilter({ ...filter, type: v })}>
            <SelectTrigger className="w-[120px]">类型</SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部</SelectItem>
              <SelectItem value="私立">私立</SelectItem>
              <SelectItem value="直资">直资</SelectItem>
              <SelectItem value="官立">官立</SelectItem>
            </SelectContent>
          </Select>

          <Select onValueChange={(v) => setFilter({ ...filter, sort: v })}>
            <SelectTrigger className="w-[140px]">排序</SelectTrigger>
            <SelectContent>
              <SelectItem value="none">默认排序</SelectItem>
              <SelectItem value="band">按升Band比例</SelectItem>
              <SelectItem value="fee">按学费高低</SelectItem>
              <SelectItem value="district">按区域</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Mobile Filter Drawer */}
        <div className="md:hidden">
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="outline" size="sm" className="flex items-center gap-2">
                <SlidersHorizontal className="w-4 h-4" /> 筛选与排序
              </Button>
            </SheetTrigger>
            <SheetContent side="bottom" className="p-6 space-y-4">
              <h3 className="text-lg font-semibold mb-3">筛选条件</h3>
              <Select onValueChange={(v) => setFilter({ ...filter, district: v })}>
                <SelectTrigger className="w-full">区域</SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">全部</SelectItem>
                  <SelectItem value="中西区">香港岛</SelectItem>
                  <SelectItem value="九龙城区">九龙</SelectItem>
                  <SelectItem value="新界">新界</SelectItem>
                </SelectContent>
              </Select>
              <Select onValueChange={(v) => setFilter({ ...filter, type: v })}>
                <SelectTrigger className="w-full">类型</SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">全部</SelectItem>
                  <SelectItem value="私立">私立</SelectItem>
                  <SelectItem value="直资">直资</SelectItem>
                  <SelectItem value="官立">官立</SelectItem>
                </SelectContent>
              </Select>
              <Select onValueChange={(v) => setFilter({ ...filter, sort: v })}>
                <SelectTrigger className="w-full">排序</SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">默认排序</SelectItem>
                  <SelectItem value="band">按升Band比例</SelectItem>
                  <SelectItem value="fee">按学费高低</SelectItem>
                </SelectContent>
              </Select>
              <Button className="w-full mt-4">应用筛选</Button>
            </SheetContent>
          </Sheet>
        </div>

        <p className="text-sm text-gray-500 mt-2 md:mt-0">共 {filteredSchools.length} 所学校</p>
      </div>

      {/* School Cards */}
      <div className="max-w-5xl mx-auto py-8 px-4 space-y-5">
        {filteredSchools.map((school, i) => (
          <motion.div
            key={i}
            whileHover={{ scale: 1.02 }}
            transition={{ type: "spring", stiffness: 200 }}
          >
            <Card className="rounded-2xl shadow-sm border border-gray-200">
              <CardContent className="p-5 space-y-2">
                <h2 className="text-lg font-semibold text-gray-900">{school.name}</h2>
                <p className="text-sm text-gray-600">{school.district} ｜ {school.type}</p>
                <p className="text-sm text-gray-700">学费：<span className="font-medium">${school.fee.toLocaleString()}</span></p>
                <p className="text-sm text-gray-700">直属中学：{school.secondary}</p>
                <div className="flex justify-between items-center mt-3">
                  <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-medium">
                    升 Band 1 比例：{school.band}%
                  </span>
                  <Button variant="outline" size="sm">详情 →</Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
