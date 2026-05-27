/**
 * static/js/scripts.js
 * =====================
 * Handles checkbox-driven habit completion without full page reloads.
 *
 * Improvements over original:
 *   - Reads CSRF token from <meta name="csrf-token"> (more robust than cookie parsing)
 *   - URL paths updated to match new url patterns (/habit/complete/, /habit/undo-complete/)
 *   - Visual feedback: completed habits get a strikethrough class
 *   - Streak count in the label is updated live from the JSON response
 */

document.addEventListener('DOMContentLoaded', function () {

    // Use event delegation so dynamically moved items still respond
    document.body.addEventListener('change', function (event) {
        if (event.target.classList.contains('habit-checkbox')) {
            handleHabitCompletion(event.target);
        }
    });

    async function handleHabitCompletion(checkbox) {
        const listItem = checkbox.closest('.habit-item');
        const habitId  = listItem.dataset.habitId;
        const isChecked = checkbox.checked;

        const url = isChecked
            ? `/habit/complete/${habitId}/`
            : `/habit/undo-complete/${habitId}/`;

        try {
            const response = await fetch(url, {
                method:  'POST',
                headers: {
                    'X-CSRFToken':   getCSRFToken(),
                    'Content-Type':  'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`Server responded with ${response.status}`);
            }

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || 'Failed to update habit');
            }

            updateUI(listItem, isChecked, data.current_streak);

        } catch (error) {
            console.error('Habit update failed:', error);
            checkbox.checked = !isChecked;  // revert the visual state
            showToast('Could not update habit. Please try again.', 'error');
        }
    }

    function getCSRFToken() {
        // Primary: read from the <meta name="csrf-token"> tag in base.html
        const meta = document.querySelector('meta[name="csrf-token"]');
        if (meta) return meta.getAttribute('content');

        // Fallback: parse from cookie
        const cookie = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : '';
    }

    function updateUI(listItem, isCompleted, newStreak) {
        const incompleteList = document.getElementById('incomplete-habits');
        const completedList  = document.getElementById('completed-habits');
        const nameEl         = listItem.querySelector('.habit-name');
        const streakEls      = listItem.querySelectorAll('p.text-sm');

        if (isCompleted) {
            // Move to completed list
            completedList.prepend(listItem);
            listItem.dataset.completed = 'true';
            listItem.classList.replace('bg-white', 'bg-green-50');
            listItem.classList.replace('border-gray-100', 'border-green-100');
            if (nameEl) nameEl.classList.add('line-through', 'text-gray-400');
        } else {
            // Move back to incomplete list
            incompleteList.prepend(listItem);
            listItem.dataset.completed = 'false';
            listItem.classList.replace('bg-green-50', 'bg-white');
            listItem.classList.replace('border-green-100', 'border-gray-100');
            if (nameEl) nameEl.classList.remove('line-through', 'text-gray-400');
        }

        // Update streak display if present
        if (newStreak !== undefined && streakEls.length > 0) {
            const streakEl = streakEls[0];
            streakEl.textContent = streakEl.textContent.replace(/\d+/, newStreak);
        }
    }

    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        const bg    = type === 'error' ? 'bg-red-600' : 'bg-gray-800';
        toast.className = `fixed bottom-6 left-1/2 -translate-x-1/2 ${bg} text-white px-6 py-3 rounded-xl shadow-lg text-sm font-medium z-50 transition-opacity duration-500`;
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 500);
        }, 3000);
    }

});
