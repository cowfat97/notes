#
# @lc app=leetcode.cn id=13 lang=python3
#
# [13] 罗马数字转整数
#

# @lc code=start
class Solution:
    def romanToInt(self, s: str) -> int:
        # 定义映射表 罗马：整数
        roman_map = {
            'I': 1,
            'V': 5,
            'X': 10,
            'L': 50,
            'C': 100,
            'D': 500,
            'M': 1000
        }

        total = 0

        # 循环输入字符串(罗马数字)
        for i in range(len(s)):
            # 获取 key
            key = s[i]

            next_key = s[i + 1] if i + 1 < len(s) else None
            # 匹配词表
            value = roman_map[key]

            next_value = roman_map[next_key] if next_key else None

            if next_value and value < next_value:
                total -= value
                continue

            total += value


        return total
# @lc code=end

