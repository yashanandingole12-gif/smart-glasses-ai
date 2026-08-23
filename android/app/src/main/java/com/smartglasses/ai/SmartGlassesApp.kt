package com.smartglasses.ai

import android.app.Application
import com.smartglasses.ai.core.network.BackendConfig

class SmartGlassesApp : Application() {
    override fun onCreate() {
        super.onCreate()
        BackendConfig.init(this)
    }
}
