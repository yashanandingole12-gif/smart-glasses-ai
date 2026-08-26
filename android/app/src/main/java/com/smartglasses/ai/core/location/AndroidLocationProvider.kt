package com.smartglasses.ai.core.location

import android.annotation.SuppressLint
import android.content.Context
import android.location.Geocoder
import android.location.Location
import com.google.android.gms.location.FusedLocationProviderClient
import com.google.android.gms.location.LocationServices
import com.google.android.gms.location.Priority
import com.google.android.gms.tasks.CancellationTokenSource
import com.google.android.gms.tasks.Tasks
import com.smartglasses.ai.core.permissions.PermissionManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.withContext
import java.util.Locale
import java.util.concurrent.TimeUnit

data class LocationInfo(
    val latitude: Double? = null,
    val longitude: Double? = null,
    val city: String = "Unavailable",
    val country: String = "",
    val isAvailable: Boolean = false
)

interface LocationProvider {
    val locationState: StateFlow<LocationInfo>
    suspend fun refreshLocation(): LocationInfo
}

class AndroidLocationProvider(private val context: Context) : LocationProvider {
    private val fusedLocationClient: FusedLocationProviderClient =
        LocationServices.getFusedLocationProviderClient(context)

    private val _locationState = MutableStateFlow(LocationInfo())
    override val locationState: StateFlow<LocationInfo> = _locationState.asStateFlow()

    @SuppressLint("MissingPermission")
    override suspend fun refreshLocation(): LocationInfo = withContext(Dispatchers.IO) {
        if (!PermissionManager.hasLocationPermission(context)) {
            val unavailable = LocationInfo(
                latitude = null,
                longitude = null,
                city = "Unavailable",
                country = "",
                isAvailable = false
            )
            _locationState.value = unavailable
            return@withContext unavailable
        }

        try {
            val cts = CancellationTokenSource()
            val location: Location? = try {
                val currentTask = fusedLocationClient.getCurrentLocation(
                    Priority.PRIORITY_BALANCED_POWER_ACCURACY,
                    cts.token
                )
                Tasks.await(currentTask, 3, TimeUnit.SECONDS) ?: run {
                    val lastTask = fusedLocationClient.lastLocation
                    Tasks.await(lastTask, 2, TimeUnit.SECONDS)
                }
            } catch (_: Exception) {
                null
            }

            if (location != null) {
                var city = "Current Location"
                var country = ""
                try {
                    val geocoder = Geocoder(context, Locale.getDefault())
                    @Suppress("DEPRECATION")
                    val addresses = geocoder.getFromLocation(location.latitude, location.longitude, 1)
                    if (!addresses.isNullOrEmpty()) {
                        val addr = addresses[0]
                        city = addr.locality ?: addr.subAdminArea ?: addr.adminArea ?: "Current Location"
                        country = addr.countryName ?: ""
                    }
                } catch (_: Exception) {
                    // Reverse geocoding network error
                }

                val newLoc = LocationInfo(
                    latitude = location.latitude,
                    longitude = location.longitude,
                    city = city,
                    country = country,
                    isAvailable = true
                )
                _locationState.value = newLoc
                return@withContext newLoc
            }
        } catch (_: Exception) {
            // Location fetch failed
        }

        val fallback = LocationInfo(isAvailable = false, city = "Unavailable")
        _locationState.value = fallback
        return@withContext fallback
    }
}
