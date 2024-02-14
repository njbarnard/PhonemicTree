#ifndef PHONEMIC_TREE_H
#define PHONEMIC_TREE_H

#include <vector>
#include <string>


using phoneme = std::array<char, 3>;
using phonemes = std::vector<phoneme>;

// The minimum number of phoneme edits (insertions, deletions or substitutions) required to change one word into the other
int extended_rhymer::levenshtein_distance(const phonemes& a, const phonemes& b) {
    size_t m = a.size();
    size_t n = b.size();

    std::vector<std::vector<int>> dp(m + 1, std::vector<int>(n + 1, 0));

    for (size_t i = 1; i <= m; i++) {
        dp[i][0] = static_cast<int>(i);
    }

    for (size_t j = 1; j <= n; j++) {
        dp[0][j] = static_cast<int>(j);
    }

    for (size_t i = 1; i <= m; i++) {
        for (size_t j = 1; j <= n; j++) {
            if (a[i - 1] == b[j - 1]) {
                dp[i][j] = dp[i - 1][j - 1];
            } else {
                dp[i][j] = std::min({ dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1] }) + 1;
            }
        }
    }

    return dp[m][n];
}


#endif //PHONEMIC_TREE_H
