package nl.sequels.game1024

import android.app.Activity
import android.content.Context
import android.os.Bundle
import android.os.VibrationEffect
import android.os.Vibrator
import android.view.WindowManager

class MainActivity : Activity(), GameView.Listener {
    private lateinit var game: Game
    private var vibrator: Vibrator? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        vibrator = getSystemService(Vibrator::class.java)
        game = Game()
        game.best = prefs().getInt("best1024", 0)
        setContentView(GameView(this, game, this))
    }

    private fun prefs() = getSharedPreferences("game1024", Context.MODE_PRIVATE)

    // Haptic feedback instead of sound effects
    override fun onMerge() = buzz(VibrationEffect.createPredefined(VibrationEffect.EFFECT_TICK))
    override fun onRotate() = buzz(VibrationEffect.createPredefined(VibrationEffect.EFFECT_CLICK))
    override fun onWin() = buzz(VibrationEffect.createWaveform(longArrayOf(0, 60, 60, 60, 60, 200), -1))
    override fun onGameOver() = buzz(VibrationEffect.createWaveform(longArrayOf(0, 250, 80, 400), -1))
    override fun onBestChanged(best: Int) { prefs().edit().putInt("best1024", best).apply() }

    private fun buzz(effect: VibrationEffect) {
        try { vibrator?.vibrate(effect) } catch (_: Exception) {}
    }
}
