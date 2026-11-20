package nl.sequels.game1024

import kotlin.random.Random

enum class Dir { LEFT, RIGHT, UP, DOWN }

/**
 * Pure game logic (no Android). Tiles store exponents: 1 => 2, 2 => 4, ... 10 => 1024,
 * like the Python and Tizen versions. 0 means empty.
 */
class Game(val n: Int = 4, private val rnd: Random = Random.Default) {
    companion object { const val WIN = 10 }

    var grid: Array<IntArray> = emptyGrid()
        private set
    var score = 0
        private set
    var best = 0
    var over = false
        private set
    var won = false          // reached 1024 and has not chosen to continue yet
        private set
    private var keepPlaying = false

    /** One tile travelling during a move. [absorbed] tiles vanish into their target cell. */
    class Slide(val fromR: Int, val fromC: Int, val toR: Int, val toC: Int, val value: Int, val absorbed: Boolean)

    class Result(
        val slides: List<Slide>,
        val merges: List<Pair<Int, Int>>,   // cells where two tiles merged
        val spawn: Pair<Int, Int>?,         // cell of the new random tile
        val reachedWin: Boolean,
        val gameOver: Boolean
    )

    private fun emptyGrid() = Array(n) { IntArray(n) }

    init { newGame() }

    fun newGame() {
        grid = emptyGrid()
        score = 0; over = false; won = false; keepPlaying = false
        spawn(); spawn()
    }

    fun continueAfterWin() { won = false; keepPlaying = true }

    private fun spawn(): Pair<Int, Int>? {
        val empty = ArrayList<Pair<Int, Int>>()
        for (r in 0 until n) for (c in 0 until n) if (grid[r][c] == 0) empty.add(r to c)
        if (empty.isEmpty()) return null
        val p = empty[rnd.nextInt(empty.size)]
        grid[p.first][p.second] = if (rnd.nextBoolean()) 1 else 2      // 2 or 4
        return p
    }

    /** Cell (row, col) at position j along line k for a direction. */
    private fun lineCell(dir: Dir, k: Int, j: Int): Pair<Int, Int> = when (dir) {
        Dir.LEFT -> k to j
        Dir.RIGHT -> k to (n - 1 - j)
        Dir.UP -> j to k
        Dir.DOWN -> (n - 1 - j) to k
    }

    /** Performs a move; returns null when nothing moved (or the game is blocked). */
    fun move(dir: Dir): Result? {
        if (over || won) return null
        val next = emptyGrid()
        val slides = ArrayList<Slide>()
        val merges = ArrayList<Pair<Int, Int>>()
        var gained = 0
        var changed = false
        var reached = false

        for (k in 0 until n) {
            val line = ArrayList<Triple<Int, Int, Int>>()          // row, col, value
            for (j in 0 until n) {
                val (r, c) = lineCell(dir, k, j)
                if (grid[r][c] != 0) line.add(Triple(r, c, grid[r][c]))
            }
            var slot = 0
            var i = 0
            while (i < line.size) {
                val (r, c, v) = line[i]
                val (tr, tc) = lineCell(dir, k, slot)
                if (i + 1 < line.size && line[i + 1].third == v) {
                    val o = line[i + 1]
                    next[tr][tc] = v + 1
                    gained += 1 shl (v + 1)
                    if (v + 1 == WIN) reached = true
                    slides.add(Slide(r, c, tr, tc, v, false))
                    slides.add(Slide(o.first, o.second, tr, tc, v, true))
                    merges.add(tr to tc)
                    changed = true
                    i += 2
                } else {
                    next[tr][tc] = v
                    slides.add(Slide(r, c, tr, tc, v, false))
                    if (r != tr || c != tc) changed = true
                    i++
                }
                slot++
            }
        }
        if (!changed) return null

        grid = next
        score += gained
        if (score > best) best = score
        val sp = spawn()
        val win = reached && !keepPlaying
        if (win) won = true else if (!canMove()) over = true
        return Result(slides, merges, sp, win, over)
    }

    private fun canMove(): Boolean {
        for (r in 0 until n) for (c in 0 until n) {
            if (grid[r][c] == 0) return true
            if (c + 1 < n && grid[r][c] == grid[r][c + 1]) return true
            if (r + 1 < n && grid[r][c] == grid[r + 1][c]) return true
        }
        return false
    }
}
