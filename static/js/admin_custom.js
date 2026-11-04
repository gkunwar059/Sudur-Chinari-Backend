/**
 * Sudur Chinari Django Admin Custom Scripts
 * - Auto-scrolls the sidebar to the active navigation link on page load
 * - Ensures active link visibility across long menu trees
 */
(function ($) {
    'use strict';

    function scrollToActiveLink() {
        var $sidebarWrapper = $('.app-sidebar .sidebar-wrapper, #jazzy-sidebar .sidebar-wrapper, .sidebar-wrapper');
        if (!$sidebarWrapper.length) {
            return;
        }

        // 1. Find active link in sidebar
        var $activeLink = $('#jazzy-navigation a.nav-link.active, .sidebar-wrapper a.nav-link.active, .sidebar-menu a.nav-link.active');

        // 2. Fallback: If Jazzmin has not assigned .active yet, match by current URL pathname
        if (!$activeLink.length) {
            var currentPath = window.location.pathname;
            var $bestMatch = null;
            var bestLen = 0;

            $('#jazzy-navigation a.nav-link').each(function () {
                var href = $(this).attr('href');
                if (href && href !== '#' && href !== 'javascript:void(0)') {
                    if (currentPath === href) {
                        $bestMatch = $(this);
                        return false;
                    } else if (currentPath.indexOf(href) === 0 && href !== '/admin/' && href.length > bestLen) {
                        $bestMatch = $(this);
                        bestLen = href.length;
                    }
                }
            });

            if ($bestMatch && $bestMatch.length) {
                $bestMatch.addClass('active');
                $activeLink = $bestMatch;
            }
        }

        // 3. Scroll container if active link is found
        if ($activeLink.length && $activeLink.is(':visible')) {
            // Expand parent treeview if closed
            var $parentTree = $activeLink.closest('.has-treeview');
            if ($parentTree.length && !$parentTree.hasClass('menu-open')) {
                $parentTree.addClass('menu-open');
                $parentTree.children('.nav-treeview').show();
            }

            var container = $sidebarWrapper[0];
            var containerHeight = $sidebarWrapper.innerHeight() || container.clientHeight;
            var containerScrollTop = $sidebarWrapper.scrollTop();
            
            var targetOffsetTop = $activeLink.offset().top;
            var containerOffsetTop = $sidebarWrapper.offset().top;
            
            var elementRelativeTop = targetOffsetTop - containerOffsetTop;
            var targetScroll = containerScrollTop + elementRelativeTop - (containerHeight / 2) + ($activeLink.outerHeight() / 2);

            $sidebarWrapper.stop().animate({
                scrollTop: Math.max(0, targetScroll)
            }, 300);
        }
    }

    $(document).ready(function () {
        // Initial run once DOM is ready
        setTimeout(scrollToActiveLink, 100);

        // Run again after full page and fonts/assets render
        $(window).on('load', function () {
            setTimeout(scrollToActiveLink, 150);
        });
    });

})(window.jQuery || jQuery);
