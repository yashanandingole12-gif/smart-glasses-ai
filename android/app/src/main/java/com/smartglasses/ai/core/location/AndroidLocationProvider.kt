package com.smartglasses.ai.core.location

import android.annotation.SuppressLint
import android.content.Context
import android.location.Geocoder
import android.location.Location
import com.google.android.gms.location.FusedLocationProviderClient
import com.google.android.gms.location.LocationServices
import com.google.android.gms.location.Priority
import com.google.android.gms.tasks.CancellationTokenSource
import com.smartglasses.ai.core.permissions.PermissionManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.withContext
import java.util.Locale

data class LocationInfo(
    val latitude: Double = 21.1458,
    val longitude: Double = 79.0882,
    val city: String = "Nagpur",
    val country: String = "India",
    val isAvailable: Boolean = true
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
            val fallback = LocationInfo(
                latitude = 21.1458,
                longitude = 79.0882,
                city = "Nagpur",
                country = "India",
                isAvailable = true
            )
            _locationState.value = fallback
            return@withContext fallback
        }

        try {
            val cts = CancellationTokenSource()
            val location: Location? = fusedLocationClient.getCurrentLocation(
                Priority.PRIORITY_BALANCED_POWER_ACCURACY,
                cts.token
            ).result ?: fusedLocationClient.lastLocation.result

            if (location != null) {
                var city = "Nagpur"
                var country = "India"
                try {
                    val geocoder = Geocoder(context, Locale.getDefault())
                    @Suppress("DEPRECATION")
                    val addresses = geocoder.getFromLocation(location.latitude, location.longitude, 1)
                    if (!addresses.isNullOrEmpty()) {
                        val addr = addresses[0]
                        city = addr.locality ?: addr.subAdminArea ?: addr.adminArea ?: "Nagpur"
                        country = addr.countryName ?: "India"
                    }
                } catch (e: Exception) {
                    // Fallback to default names on geocoder network issue
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
        } catch (e: Exception) {
            // Log and preserve cached location
        }

        return@withContext _locationState.value
    }
}
