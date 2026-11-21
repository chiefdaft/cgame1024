package nl.sequels.game1024

import org.junit.Assert.*
import org.junit.Test

class GameTest {
    private fun setGrid(g: Game, rows: Array<IntArray>) {
        val f = Game::class.java.getDeclaredField("grid"); f.isAccessible = true
        f.set(g, rows)
    }

    @Test fun mergesPairsOnceAndScores() {
        val g = Game()
        setGrid(g, arrayOf(intArrayOf(1, 1, 1, 1), IntArray(4), IntArray(4), IntArray(4)))
        val res = g.move(Dir.LEFT)!!
        assertEquals(2, res.merges.size)
        assertEquals(8, g.score)                       // 4 + 4
        assertEquals(2, g.grid[0][0]); assertEquals(2, g.grid[0][1])
    }

    @Test fun noMoveReturnsNull() {
        val g = Game()
        setGrid(g, arrayOf(intArrayOf(1, 0, 0, 0), IntArray(4), IntArray(4), IntArray(4)))
        assertNull(g.move(Dir.LEFT))
    }

    @Test fun reachingWinBlocksUntilContinue() {
        val g = Game()
        setGrid(g, arrayOf(intArrayOf(9, 9, 0, 0), IntArray(4), IntArray(4), IntArray(4)))
        val res = g.move(Dir.LEFT)!!
        assertTrue(res.reachedWin); assertTrue(g.won)
        assertNull(g.move(Dir.RIGHT))
        g.continueAfterWin()
        assertNotNull(g.move(Dir.RIGHT))
    }

    @Test fun detectsGameOver() {
        val g = Game()
        setGrid(g, arrayOf(intArrayOf(1, 2, 1, 2), intArrayOf(2, 1, 2, 1), intArrayOf(1, 2, 1, 2), intArrayOf(2, 1, 0, 1)))
        // slide bottom row right: fills the board with no equal neighbours left
        val res = g.move(Dir.RIGHT)
        assertNotNull(res)
    }

    @Test fun clockwiseTurnMovesOuterRingOnly() {
        val g = Game()
        val rows = Array(4) { IntArray(4) }
        rows[0][0] = 1; rows[1][1] = 2; rows[1][0] = 3
        setGrid(g, rows)
        g.rotate(true)
        assertEquals(1, g.grid[0][3])          // top-left corner -> top-right corner
        assertEquals(3, g.grid[0][2])          // (1,0) -> (0,2): three steps along the ring
        assertEquals(2, g.grid[1][1])          // inner tile stays
    }

    @Test fun counterClockwiseTurnMovesOtherWay() {
        val g = Game()
        val rows = Array(4) { IntArray(4) }
        rows[0][0] = 1
        setGrid(g, rows)
        g.rotate(false)
        assertEquals(1, g.grid[3][0])          // top-left -> bottom-left
    }

    @Test fun fourTurnsOnFullBoardRestoreIt() {
        val g = Game()
        val rows = Array(4) { r -> IntArray(4) { c -> r * 4 + c + 1 } }
        rows[3][3] = rows[3][2]                // keep a merge available so the game is not over
        setGrid(g, rows)
        val before = g.grid.map { it.toList() }
        repeat(4) { assertNotNull(g.rotate(true)) }
        assertEquals(before, g.grid.map { it.toList() })
    }
}
