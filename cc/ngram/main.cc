#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>
#include <tuple>
#include <map>
#include <fstream>

class NGramModel {
  /**
   * Known tokens.
   */
  std::vector<std::string> tokens;

  /**
   * Build index for every known tokens.
   */
  std::unordered_map<std::string, size_t> indexer;

  /**
   * Each key is n - 1 tokens
   * Each value is a vector, each element in the vector contains a pair of values, indicating
   * the index of the next token, and for how many times this combination occurs.
   */
  std::map<std::vector<std::size_t>, std::unordered_map<size_t, size_t>> pred;

  int n;
public:
  NGramModel(int _n) {
    n = _n;
  }

  void train(const std::vector<std::string> &passage) {
    /** Build index for whole passage */
    std::vector<size_t> indexed_passage;
    for (const auto &token : passage) {
      if (!indexer.count(token)) {
        indexer[token] = tokens.size();;
        tokens.emplace_back(token);
      }
      indexed_passage.push_back(indexer[token]);
    }

    /** Learning the probability */
    for (auto i = 0; i + n < indexed_passage.size(); i++) {
      std::vector<size_t> prev_tokens;
      size_t next_token = indexed_passage[i + n];
      for (int j = 0; j < n - 1; j++) {
        prev_tokens.push_back(indexed_passage[i + j]);
      }
      pred[prev_tokens][next_token] += 1;
    }
  }

  int predict(const std::vector<size_t> &prev_tokens) {
    if (pred.count(prev_tokens)) {
      size_t max_count = 0;
      size_t ans = 0;
      for (const auto &p : pred[prev_tokens]) {
        if (p.second > max_count) {
          ans = p.first;
        }
      }
      return ans;
    } else {
      return 0;
    }
  }
};

class Parser {

};


int main(const int argc, const char *argv[]) {
  std::ifstream in(argv[1]);
}