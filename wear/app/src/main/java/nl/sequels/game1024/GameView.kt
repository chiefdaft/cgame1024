package nl.sequels.game1024

import android.animation.ValueAnimator
import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.RectF
import android.graphics.Typeface
import android.view.InputDevice
import android.view.MotionEvent
import android.view.View
import kotlin.math.abs
import kotlin.math.min
import kotlin.math.sin

/** Draws the board on the (round) watch face and turns swipes/taps into game moves. */
class GameView(context: Context, private val game: Game, private val listener: Listener) : View(context) {

    interface Listener {
        fun onMerge()
        fun onRotate()
        fun onWin()
        fun onGameOver()
        fun onBestChanged(best: Int)
    }

    private companion object {
        const val SLIDE_END = 0.6f           // fraction of the animation spent sliding
        const val ANIM_MS = 180L
        const val ROT_STEP = 1f              // accumulated bezel scroll needed for one quarter turn
        val COLORS = intArrayOf(
            0, 0xFF00FFFF.toInt(), 0xFFFFFFFF.toInt(), 0xFFE6E6E6.toInt(), 0xFFFF3B3B.toInt(),
            0xFF3BFF3B.toInt(), 0xFFFF7F00.toInt(), 0xFF4A6BFF.toInt(), 0xFFA020A0.toInt(),
            0xFFFF00FF.toInt(), 0xFFFFD700.toInt(), 0xFFFFD700.toInt()
        )
        val BOARD_BG = 0xFF1C1C1C.toInt()
        val CELL_BG = 0xFF2A2A2A.toInt()
        val ORANGE = 0xFFFF7F00.toInt()
        val GOLD = 0xFFFFD700.toInt()
    }

    private val fill = Paint(Paint.ANTI_ALIAS_FLAG)
    private val text = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        typeface = Typeface.DEFAULT_BOLD
        textAlign = Paint.Align.CENTER
    }
    private val rect = RectF()

    // animation state of the last move
    private var slides: List<Game.Slide> = emptyList()
    private var merges: List<Pair<Int, Int>> = emptyList()
    private var spawn: Pair<Int, Int>? = null
    private var t = 1f
    private val animator = ValueAnimator.ofFloat(0f, 1f).apply {
        duration = ANIM_MS
        addUpdateListener { t = it.animatedValue as Float; invalidate() }
    }

    // board geometry, recomputed in onDraw
    private var left = 0f
    private var top = 0f
    private var gap = 0f
    private var cell = 0f

    private var rotAcc = 0f

    init { isFocusable = true; isFocusableInTouchMode = true }

    override fun onAttachedToWindow() { super.onAttachedToWindow(); requestFocus() }

    private var downX = 0f
    private var downY = 0f

    private fun cellX(c: Float) = left + gap + c * (cell + gap)
    private fun cellY(r: Float) = top + gap + r * (cell + gap)

    override fun onDraw(canvas: Canvas) {
        val w = width.toFloat()
        val h = height.toFloat()
        val d = min(w, h)
        canvas.drawColor(Color.BLACK)

        // A square board that fits inside the round display with room for score above and below.
        val side = d * 0.70f
        left = (w - side) / 2
        top = (h - side) / 2
        gap = side * 0.03f
        cell = (side - gap * 5) / 4

        fill.color = BOARD_BG
        rect.set(left, top, left + side, top + side)
        canvas.drawRoundRect(rect, gap * 2, gap * 2, fill)
        fill.color = CELL_BG
        for (r in 0 until 4) for (c in 0 until 4) {
            rect.set(cellX(c.toFloat()), cellY(r.toFloat()), cellX(c.toFloat()) + cell, cellY(r.toFloat()) + cell)
            canvas.drawRoundRect(rect, gap, gap, fill)
        }

        if (t < SLIDE_END) {
            val p = ease(t / SLIDE_END)
            for (s in slides) {
                var r = s.fromR + (s.toR - s.fromR) * p
                var c = s.fromC + (s.toC - s.fromC) * p
                if (s.ringFrom >= 0) {                      // follow the ring around the corners
                    val f = s.ringFrom + s.ringSteps * p
                    val i0 = Math.floor(f.toDouble()).toInt()
                    val fr = f - i0
                    val a = game.ringCell(i0)
                    val b = game.ringCell(i0 + 1)
                    r = a.first + (b.first - a.first) * fr
                    c = a.second + (b.second - a.second) * fr
                }
                drawTile(canvas, s.value, c, r, 1f)
            }
        } else {
            val u = ((t - SLIDE_END) / (1f - SLIDE_END)).coerceIn(0f, 1f)
            for (r in 0 until 4) for (c in 0 until 4) {
                val v = game.grid[r][c]
                if (v == 0) continue
                var scale = 1f
                if (merges.contains(r to c)) scale = 1f + 0.14f * sin(Math.PI.toFloat() * u)
                if (spawn == r to c) scale = u
                drawTile(canvas, v, c.toFloat(), r.toFloat(), scale)
            }
        }

        // current score above, best score below the board
        text.color = Color.WHITE
        text.textSize = d * 0.09f
        drawCentered(canvas, game.score.toString(), w / 2, top / 2)
        text.color = GOLD
        text.textSize = d * 0.065f
        drawCentered(canvas, "BEST ${game.best}", w / 2, top + side + (h - top - side) / 2)

        if (game.over) drawOverlay(canvas, "GAME OVER", "Tap to restart", d)
        else if (game.won) drawOverlay(canvas, "YOU WIN!", "Tap to continue", d)
    }

    private fun drawTile(canvas: Canvas, v: Int, col: Float, row: Float, scale: Float) {
        if (scale <= 0f) return
        val cx = cellX(col) + cell / 2
        val cy = cellY(row) + cell / 2
        val half = cell / 2 * scale
        fill.color = COLORS[min(v, 11)]
        rect.set(cx - half, cy - half, cx + half, cy + half)
        canvas.drawRoundRect(rect, gap * scale, gap * scale, fill)

        val label = (1 shl v).toString()
        text.color = if (v == 7 || v == 8) Color.WHITE else 0xFF111111.toInt()
        text.textSize = cell * scale * when (label.length) { 1 -> 0.55f; 2 -> 0.5f; 3 -> 0.4f; else -> 0.33f }
        drawCentered(canvas, label, cx, cy)
    }

    private fun drawCentered(canvas: Canvas, s: String, cx: Float, cy: Float) {
        val fm = text.fontMetrics
        canvas.drawText(s, cx, cy - (fm.ascent + fm.descent) / 2, text)
    }

    private fun drawOverlay(canvas: Canvas, title: String, sub: String, d: Float) {
        fill.color = 0xB3000000.toInt()
        canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), fill)
        val bw = d * 0.78f
        val bh = d * 0.32f
        fill.color = ORANGE
        rect.set((width - bw) / 2, (height - bh) / 2, (width + bw) / 2, (height + bh) / 2)
        canvas.drawRoundRect(rect, d * 0.05f, d * 0.05f, fill)
        text.color = Color.BLACK
        text.textSize = d * 0.095f
        drawCentered(canvas, title, width / 2f, height / 2f - bh * 0.17f)
        text.textSize = d * 0.058f
        drawCentered(canvas, sub, width / 2f, height / 2f + bh * 0.22f)
    }

    private fun ease(x: Float) = x * (2 - x)

    private fun play(dir: Dir) = apply(game.move(dir), rotation = false)

    private fun rotate(clockwise: Boolean) = apply(game.rotate(clockwise), rotation = true)

    private fun apply(res: Game.Result?, rotation: Boolean) {
        if (res == null) return
        val before = game.best
        slides = res.slides
        merges = res.merges
        spawn = res.spawn
        animator.cancel()
        animator.start()
        if (rotation) listener.onRotate()
        if (res.merges.isNotEmpty()) listener.onMerge()
        if (game.best != before) listener.onBestChanged(game.best)
        if (res.reachedWin) listener.onWin() else if (res.gameOver) listener.onGameOver()
    }

    private fun tap() {
        if (game.over) game.newGame()
        else if (game.won) game.continueAfterWin()
        else return
        slides = emptyList(); merges = emptyList(); spawn = null
        animator.cancel(); t = 1f
        invalidate()
    }

    override fun onTouchEvent(e: MotionEvent): Boolean {
        when (e.actionMasked) {
            MotionEvent.ACTION_DOWN -> { downX = e.x; downY = e.y }
            MotionEvent.ACTION_UP -> {
                val dx = e.x - downX
                val dy = e.y - downY
                val min = min(width, height) * 0.08f
                if (abs(dx) < min && abs(dy) < min) { tap(); performClick() }
                else if (abs(dx) > abs(dy)) play(if (dx > 0) Dir.RIGHT else Dir.LEFT)
                else play(if (dy > 0) Dir.DOWN else Dir.UP)
            }
        }
        return true
    }

    /** Rotary bezel (Galaxy Watch Classic): clockwise / counter-clockwise quarter turn of the outer ring. */
    override fun onGenericMotionEvent(e: MotionEvent): Boolean {
        if (e.action == MotionEvent.ACTION_SCROLL && e.isFromSource(InputDevice.SOURCE_ROTARY_ENCODER)) {
            rotAcc += -e.getAxisValue(MotionEvent.AXIS_SCROLL)       // clockwise => positive
            if (abs(rotAcc) >= ROT_STEP) { rotate(rotAcc > 0); rotAcc = 0f }
            return true
        }
        return super.onGenericMotionEvent(e)
    }

    override fun performClick(): Boolean = super.performClick()
}
